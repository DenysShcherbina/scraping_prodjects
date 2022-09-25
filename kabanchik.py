import requests
import time
import os.path
import json
from requests.exceptions import ConnectionError


class Parse:

    def __init__(self):
        self.headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 '
                                      '(KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36'}
        self.headers_for_photo = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'}
        self.result_dicts = []
        self.count = 1

    # Collect data about performers
    def collect_data(self):
        for page in range(1, 100):
            url = f'https://kiev.kabanchik.ua/ua/perfs-rating?category=963&region=null&page={page}'
            response = requests.get(url=url, headers=self.headers)
            response.encoding = 'utf-8'
            response = response.json()
            if not response['data']['performers']:
                print('Last page')
                break
            for i in response['data']['performers']:
                self.result_dicts.append({
                    'name': i["name"],
                    'url': i["user_id"],
                    'foto': i['performer_id'],
                    'description': i['about_info']})

            time.sleep(1)

    # Save data about performers in json
    def save_json(self):
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(self.result_dicts, f, indent=4, ensure_ascii=False)

    # Create directory if not exists
    @staticmethod
    def create_directory(data):
        name_dir = str(data['url'])
        if not os.path.exists(name_dir):
            os.mkdir(name_dir)
        return name_dir

    def get_data_from_site(self):
        for data in self.result_dicts:
            print(f'### Starting collect data at page {self.count} / {len(self.result_dicts)}')
            self.count += 1

            name_dir = self.create_directory(data)

            # Download description
            with open(f'{name_dir}\\info.txt', 'w', encoding='utf-8') as f:
                f.write(f'{data["name"].strip()}\n\n')
                if not data['description']:
                    f.write('No description.')
                else:
                    f.write(data['description'].strip())

            # Download photo
            for page in range(1, 12321):
                link = f'https://kabanchik.ua/ua/performer/{data["foto"]}/portfolio-photos?&page={page}&limit=50'
                response = requests.get(url=link, headers=self.headers_for_photo).json()
                if not response['data']:
                    print('No photos')
                    break
                for block in response['data']:
                    if block['type'] == 'image':
                        name_file = block['name']
                        try:
                            picture = requests.get(url=block['url'], headers=self.headers, timeout=15)
                        except ConnectionError as err:
                            print(repr(err))
                            print(f"Err was find at {block['url']}, which must be at directory {name_dir}")
                            continue
                        if os.path.isfile(f'{name_dir}\\{block["name"]}'):
                            name_file = "(02)" + name_file
                        with open(f'{name_dir}\\{name_file}', 'wb') as f:
                            f.write(picture.content)
                            time.sleep(0.5)
            time.sleep(2)


if __name__ == '__main__':
    p = Parse()
    p.collect_data()
    p.save_json()
    # with open('data.json', 'r', encoding='utf-8') as f:
    #     [p.result_dicts.append(i) for i in json.load(f)]
    p.get_data_from_site()
