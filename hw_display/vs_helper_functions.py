import requests
from bs4 import BeautifulSoup


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
ARCHIVE_ROOT = 'https://viescolaire.ecolejeanninemanuel.net/cahiers/'


class InvalidCredentials(Exception):
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
        self.data_dict = {}
        self.subjects = {str(x.text): x['value'] for x in self.data.find(id="devMatChoice").find_all('option')}
        # Get homework titles and ids
        for div in self.data.findAll(class_='left'):
            for a in div.findAll('a'):
                title = a.findAll('strong')
                if title:
                    a = str(a)
                    _id = a.split('?')[1].replace('">', '')
                    self.data_dict[_id] = {}

    # Get homework details
    def get_content(self, _id):  # format: _id = "id=1234"
        href = 'https://viescolaire.ecolejeanninemanuel.net/cahiers/e_vw_devoir.php?'
        info = self.session.get(href + _id, headers=HEADERS)
        details = BeautifulSoup(info.content, 'html.parser')
        content = details.text.replace('\t', '').replace('\r', '').replace('\xa0', ' ')
        content1, content2 = content.split("Temps moyen estimé")
        content1 = [_ for _ in content1.split('\n') if _]
        content2 = content2.split('\n')
        content2 = [content2[_] for _ in range(len(content2)) if content2[_] or content2[_ - 1]]
        content = content1 + ['Temps'] + content2
        return content

    def get_content_sorted(self, _id):
        content = self.get_content(_id)
        # 0 - 11: index
        # 12: Subject
        # 13: Title
        # 14, 15: Class date, value
        # 16, 17: Due date, value: MM/DD/YYYY(X jours)
        # 18, 19: Time estimated, value
        # 20 - end: description
        if len(content) > 10:
            if content[12] != "Date du cours:":
                title = content[13]
                subject = content[12]
                date_class = content[15]
                date_due = content[17].split('(')[0]
                time_est = content[19]
                days_left = content[17].split('(')[1].replace(' jours)', '')
                description = [content[i] for i in range(20, len(content) - 1)]
                description = '<br />'.join(description)
                # Store content inside data dict
                if _id not in self.data_dict:
                    # necessary for fetching ids not in our hw
                    self.data_dict[_id] = {}
                stored = self.data_dict[_id]  # index
                stored['id'] = int(_id.split('\n')[0][3:])
                stored['title'] = title  # 0
                # `if` necessary for MPS, SES, etc
                stored['subject'] = subject.lower().capitalize() if len(subject) > 3 else subject.upper()  # 1
                stored['date_class'] = date_class  # 2
                stored['date_due'] = date_due  # 3
                stored['days_left'] = days_left  # 4
                stored['time_est'] = time_est if time_est != '-' else None # 5
                stored['description'] = description  # 6
                return stored

    def get_all(self):
        for hw in self.data_dict.keys():
            self.get_content_sorted(hw)
        return sorted(self.data_dict.items(), key=lambda x: (int(x[1]['days_left']), x[1]['subject']))

    def get_hw_by_id(self, _id):
        return self.get_content_sorted('id={}'.format(_id))

    def get_hw_archives(self, link):
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
                            temp_dict[key] = values.replace('\t', '').replace('\r', '').replace('\n', '')
            hw_archive.append(temp_dict)
        return subject, hw_archive
