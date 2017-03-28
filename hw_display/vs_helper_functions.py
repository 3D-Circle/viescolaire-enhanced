import requests
from bs4 import BeautifulSoup


class InvalidCredentials(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class Homework(object):
    def __init__(self, payload):  # payload = get_login()
        self.session = requests.session()
        post = self.session.post('https://viescolaire.ecolejeanninemanuel.net/auth.php', data=payload)
        self.data = BeautifulSoup(post.content, "html.parser")

        if "Erreur" in self.data.text:
            raise InvalidCredentials("Login error - invalid credentials.")

        # homework dictionary
        self.data_dict = {}

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
        info = self.session.get(href + _id)
        details = BeautifulSoup(info.content, 'html.parser')
        content = details.text.replace('\t', '').replace('\r', '').replace('\xa0', ' ')
        content1, content2 = content.split("Temps moyen estimé")
        content1 = [_ for _ in content1.split('\n') if _]
        content2 = content2.split('\n')
        content2 = [content2[_] for _ in range(len(content2)) if content2[_] or content2[_ - 1]]
        content2[-2] = "`"
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
                stored = self.data_dict[_id]  # index
                stored['title'] = title  # 0
                stored['subject'] = subject  # 1
                stored['date_class'] = date_class  # 2
                stored['date_due'] = date_due  # 3
                stored['days_left'] = days_left  # 4
                stored['time_est'] = time_est  # 5
                stored['description'] = description  # 6

    def get_all(self):
        for hw in self.data_dict.keys():
            self.get_content_sorted(hw)
        return sorted(self.data_dict.items(), key=lambda x: (int(x[1]['days_left']), x[1]['subject']))
