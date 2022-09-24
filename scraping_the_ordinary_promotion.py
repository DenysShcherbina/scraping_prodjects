import json
import requests
from bs4 import BeautifulSoup

headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36'}

#  Get all links with promotion
links = []
for page in range(0, 2500, 28):
    url = f'https://www.sephora.pl/wyniki-wyszukiwania?cgid=root&prefn1=brand&prefv1=ORDIN&srule=Manual_reve&start={page}&sz=28&format=page-element&on=onclickload'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    blocks = soup.find_all('div', class_='product-info-wrapper')
    if len(blocks) == 0:
        break
    for block in blocks:
        if block.find('span', {'class': 'product-sales-price', 'title': 'Cena promocyjna'}):
           link = block.find('a', class_='product-tile-link').get('href')
           links.append(link)

#  Get data from links
result = []
count = 1
for url in links:
    resp = requests.get(url.strip(), headers=headers)
    print(f'##{count} with url: {url} processing')
    soup = BeautifulSoup(resp.text, 'lxml')
    name = soup.find('span', class_='hide-for-medium product-name').text.replace('\n', ' ').strip()
    title = soup.find('div', class_='product-description-box').text.strip()

    # Delete some symbols from string
    for i in ['\n', '*']:
        if i in title:
            title = title.replace(i, ' ')

    usage = soup.find('li', id='tab-tips').find('div', class_='accordion-content').text.strip()
    for i in ['\n', '*']:
        if i in usage:
            usage = usage.replace(i, ' ')
    size = soup.find('a', class_='variation-display-name').get('title').strip()
    old_price = soup.find('span', class_='price-standard').text.strip()
    new_price = soup.find('span', class_='price-sales').text.strip()
    product_dict = {
            'Name': name,
            'Title': title,
            'Usage': usage,
            'Size': size,
            'Old Price': old_price,
            'New Price': new_price,
            'Link': url.strip()}

    result.append(product_dict)
    count += 1

# Save data
with open('promocia.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=4, ensure_ascii=False)
