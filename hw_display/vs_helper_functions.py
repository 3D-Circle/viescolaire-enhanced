import collections
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
ARCHIVE_ROOT = 'https://viescolaire.ecolejeanninemanuel.net/cahiers/'
WIC_ROOT = 'https://viescolaire.ecolejeanninemanuel.net/cahiers/e_archive_seance.php?'
INDIVIDUAL_WIC_ROOT = 'https://viescolaire.ecolejeanninemanuel.net/cahiers/e_vw_seance.php?ret=archive&id='
UPlOAD_ROOT = ''


class InvalidCredentials(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class PageNotFound(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class Homework(object):
    def __init__(self, payload):  # payload = get_login()
        self.session = requests.session()
        post = self.session.post(
            'https://viescolaire.ecolejeanninemanuel.net/auth.php',
            data=payload, headers=HEADERS
        )
        self.data = BeautifulSoup(post.content, "html.parser")

        if "Erreur" in self.data.text:
            raise InvalidCredentials("Login error - invalid credentials.")

        # homework dictionary
        self.hw_list = []
        self.subjects = {
            str(x.text): x['value'].split('?')[-1] for x in self.data.find(id="devMatChoice").find_all('option')
        }  # list of subjects is found in the option selector #devMatChoice

        # Get homework titles and ids
        for row in self.data.findAll('tr'):
            if row.get('class'):
                if row.get('class')[0] in ['liste_couleur1', 'liste_couleur2']:
                    for a in row.findAll('a'):
                        title = a.findAll('strong')
                        if title:
                            _id = int(a['href'].split('=')[-1])
                            self.hw_list.append(_id)

    # Get homework details
    def get_content(self, _id):  # enough with weird formats ! just keep it as an int.
        """Get all info from the _id"""
        assert type(_id) is int  # Yes we even check !
        href = 'https://viescolaire.ecolejeanninemanuel.net/cahiers/e_vw_devoir.php?id='
        info = self.session.get(f'{href}{_id}', headers=HEADERS)
        soup = BeautifulSoup(info.content, 'html.parser')
        content_table = soup.find(class_='infotbl')
        date_due, days_left = self.clean(
            content_table.find_all('tr')[1].find_all('td')[1].text, True
        ).replace(')', '').split('(')  # original format: 'dd/mm/yyy (xxx jours)'

        if '1970' in date_due:
            raise PageNotFound

        content = {
            'id': _id,
            'subject': soup.find(class_='page_title').text.lower().capitalize(),
            'date_class': content_table.find_all('tr')[0].find_all('td')[1].text, 'date_due': date_due,
            'days_left': int(days_left.split(' ')[0]),
            'time_est': content_table.find_all('tr')[2].find_all('td')[1].text,
            'title': soup.find(class_='dev_title').text,
            'description': self.clean(
                content_table.find(class_='infdesc').text
            ).strip('\n').replace('\n', '<br>'),
            'files': []
        }
        file_links = [
            i.find('a') for i in content_table.find_all(class_='infattach') if self.clean(i.find('a').text, True)
        ]
        for file_link in file_links:
            content['files'].append({
                self.clean(file_link.text, True): f"{ARCHIVE_ROOT}{file_link['href']}"
            })
        if len(content['subject']) <= 3:
            content['subject'] = content['subject'].upper()
        return content

    def get_all(self):
        """Get all hw due and sort it"""
        all_hw_dicts = [self.get_content(_id) for _id in self.hw_list]
        # nested defaultdict
        # defaultdict -> defaultdict -> list
        divided_dict = collections.defaultdict(lambda: collections.defaultdict(list))
        for single_hw in all_hw_dicts:
            day_due = datetime.now() + timedelta(days=single_hw['days_left'])
            week_number = day_due.isocalendar()[1]
            day_number = (day_due - datetime(1970, 1, 1)).days
            divided_dict[week_number][day_number].append(single_hw)
        return self.default_to_regular(divided_dict)  # sorted(all_hw_dicts, key=lambda x: x['days_left'])

    def get_hw_by_id(self, _id):
        return self.get_content(_id)

    def get_wic_by_id(self, _id):
        """Get work in class from id (wic = work in class)"""
        soup = BeautifulSoup(self.session.get(f'{INDIVIDUAL_WIC_ROOT}{_id}').content, 'html.parser')
        print(self.clean(soup.find_all('tr')[1].find_all('td')[1].text))
        return {
            'subject': soup.find_all('h4')[0].text,
            'title': soup.find_all('h4')[1].text,
            'date_class': soup.find_all('tr')[0].find_all('td')[1].text,
            'description': self.clean(
                soup.find_all('tr')[1].find_all('td')[1].text
            ).replace('\n', '<br>')
        }

    def get_hw_archives(self, link):
        """Get list of archived hw from a link (which gives the required subject info)"""
        raw_list = self.session.get(f'{ARCHIVE_ROOT}{link}', headers=HEADERS)
        soup = BeautifulSoup(raw_list.content, 'html.parser')
        rows = soup.find_all(class_='liste')[0].find_all('tr')
        subject = soup.find('h4').text.split(' ')[-1]
        hw_archive = []
        for row in rows:
            temp_dict = {}
            if row.find_all('a'):
                _id = row.find('a')
                if 'id=' in _id['href']:
                    temp_dict['id'] = int(_id['href'].split('=')[-1])
                    temp_dict['date_class'] = row.find_all('td')[0].text
                    temp_dict['title'] = row.find('a').text
                    temp_dict['teacher'] = row.find_all('td')[2].text
                    temp_dict['date_due'] = row.find_all('td')[3].text
                    temp_dict['days_left'] = row.find_all('td')[4].text.split(' ')[0]
                    for key, values in temp_dict.items():
                        if type(values) is str:
                            temp_dict[key] = self.clean(values, True)
            if temp_dict:  # check if empty
                hw_archive.append(temp_dict)
        return subject, hw_archive

    def get_wic(self, link):
        """Get list of work done in class from link"""
        raw_list = self.session.get(f'{WIC_ROOT}{link}', headers=HEADERS)
        soup = BeautifulSoup(raw_list.content, 'html.parser')
        wic_list = []

        if soup.find_all(class_='warning_err'):
            raise PageNotFound

        subject = soup.find('h4').text.split('-')[-1].strip()
        for row in soup.find_all('tr'):
            if len(row.find_all('td')) == 4:
                temp_dict = {
                    'date_class': row.find_all('td')[0].text,
                    'title': row.find_all('td')[1].text,
                    'id': row.find_all('a')[0]['href'].split('=')[-1],
                    'teacher': row.find_all('td')[2].text
                }
                wic_list.append({
                    key: self.clean(value).replace('\n', '') for key, value in temp_dict.items()
                })
        return subject, wic_list

    def change_password(self, new_password):
        self.student_id = int(
            self.data.find(id="statut").find('a')['href'].split('=')[-1]
        )  # needed for changing password
        self.session.post(f'{ARCHIVE_ROOT}user.php', data={
            'id': self.student_id,
            'mdp1': new_password,
            'mdp2': new_password
        })

    @staticmethod
    def clean(s, newlines=False):
        """Used to clean strings from scraping bouillie"""
        half_cleaned = s.replace('\t', '').replace('\r', '')
        if newlines:
            return half_cleaned.replace('\n', '')
        else:
            return half_cleaned

    def default_to_regular(self, d):
        """convert defaultdict to normal dict"""
        if isinstance(d, collections.defaultdict):
            d = {k: self.default_to_regular(v) for k, v in d.items()}
        return d

if __name__ == '__main__':
    o = Homework({'login': 't.takla19@ejm.org', 'mdp': 'EABJTT'})
    o.change_password('EABJMM')