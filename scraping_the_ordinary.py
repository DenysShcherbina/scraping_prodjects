import json
import requests
from bs4 import BeautifulSoup

headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36'}

#  Get all links
links = []
for page in range(0, 2500, 28):
    url = f'https://www.sephora.pl/wyniki-wyszukiwania?cgid=root&prefn1=brand&prefv1=ORDIN&srule=Manual_reve&start={page}&sz=28&format=page-element&on=onclickload'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    blocks = soup.find_all('div', class_='product-info-wrapper')
    if len(blocks) == 0:
        break
    for product in blocks:
        link = product.find('a', class_='product-tile-link').get('href')
        links.append(link)

# Get all data from links
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

    product_dict = {
        'Name': name,
        'Title': title,
        'Usage': usage,
        'Price': {},
        'Link': url.strip()}

    url_price = [url.get('href') for url in soup.find_all('a', class_='variation-display-name')]
    ml = [ml.get('title') for ml in soup.find_all('a', class_='variation-display-name')]
    for index, link in enumerate(url_price, start=0):
        resp = requests.get(link, headers=headers)
        price_soup = BeautifulSoup(resp.text, 'lxml')
        try:
            price = price_soup.find('span', class_='price-sales price-sales-standard').find('span').text.strip()
            product_dict['Price'][ml[index]] = price
        except AttributeError:
            price = price_soup.find('span', class_='price-sales').find('span').text.strip()
            product_dict['Price'][ml[index]] = price

    result.append(product_dict)
    count += 1

# Save data
with open('ordinary.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=4, ensure_ascii=False)
