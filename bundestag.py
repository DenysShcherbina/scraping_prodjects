import json
import requests
from bs4 import BeautifulSoup

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/103.0.0.0 Safari/537.36'}

card = 0
j_res = []
all_urls = []

# Get all urls
for page in range(0, 1500, 20):  #740
    url = f'https://www.bundestag.de/ajax/filterlist/de/abgeordnete/862712-862712?limit=20&noFilterSet=true&offset={page}'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    blocks = soup.find_all('div', class_='col-xs-4 col-sm-3 col-md-2 bt-slide')
    if not blocks:
        break
    for i in blocks:
        url = 'https://www.bundestag.de' + i.find('a').get('href')
        all_urls.append(url)

# Get data(name, company, links on social media if exists)
try:
    for url in all_urls:
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.text, 'lxml')
        name = soup.find('div', class_='col-xs-8 col-md-9 bt-biografie-name').find('h3').text.split(sep=',')
        card_dict = {'name': name[0].strip(),
                     'company': name[1].strip()}

        social_media = soup.find_all('div', class_='row')[2].find_all('li')
        for i in social_media:
            name_soc = i.find('a').get('title')
            link = i.find('a').get('href')
            card_dict[name_soc] = link

        j_res.append(card_dict)
        print(f'#{card} : {url} is done!')
        card += 1

except Exception as er:
    print(repr(er))
    print(f'Last index was done {card}')

finally:
    # Save data
    with open('3.json', 'w', encoding='utf-8') as f:
        json.dump(j_res, f, indent=4, ensure_ascii=False)
