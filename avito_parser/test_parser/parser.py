import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import time
import os

MAIN_URL = 'https://www.avito.ru'
REG_URL = 'https://www.avito.ru/krasnodarskiy_kray/kvartiry/prodam'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

FILE_CAPACITY = 2000

def get_page(url):
    try: 
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error. Dont load page: {e}")
        return None

def parse_block(item):
    try:
        title_element = item.select_one("h1[itemprop='name']")
        title = title_element.text.strip() if title_element else "Нет заголовка"

        url_element = item.select_one("a[itemprop='url']")
        relative_url = url_element.get("href") if url_element else None
        link = MAIN_URL + relative_url if relative_url else "Нет ссылки"

        price_element = item.select_one("span[itemprop='price']")
        price = price_element.get("content") if price_element else "0"

        address_element = item.select_one('a[data-marker="street_link"]')
        address = address_element.text.strip() if address_element else "Нет адреса"

        description_element = item.select_one('div[data-marker="item-view/item-description"]')
        description = description_element.text.strip() if description_element else ""
        square = extract_square(description)

        date_element = item.select_one('div[data-marker="item-date"]')
        pub_date = date_element.text.strip() if date_element else "Неизвестна"

        return {
            "title":title,
            "price": price,
            "address": address,
            "square": square,
            "link": link,
            "date": pub_date
        }
    except Exception as e:
        print(f"Error. Block Parsing: {e}")
        return None

def extract_square(text):
    import re
    match = re.search(r"(\d{1,4}\s?м²)", text)
    return match.group(1).replace(" ", "") if match else "Не указана"

def save_xml(data, index):
    root = ET.Element("announc")
    for announc in data:
        announc_element = ET.SubElement(root, "announc")
        for key, value in announc.items():
            element = ET.SubElement(announc_element, key)
            element.text = value
    
    tree = ET.ElementTree(root)
    filename = f"avito_ads_{index}.xml"
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", filename)
    tree.write(filepath, encoding="utf-8", xml_declaration=True)
    print(f"Сохранено: {filepath}")

def main():
    data = []
    files_counter = 1
    announc_counter = 0

    for page in range(1,FILE_CAPACITY + 1):
        print(f"Обработка страницы {page}")
        url = f"{REG_URL}?p={page}" 
        html = get_page(url)
        if not html:
            continue
        
        soup = BeautifulSoup(html, "lxml")
        items = soup.select("div[data-marker='item']")

        if not items:
            print("Возможно, закончились страницы")
            break

        for item in items:
            announc = parse_block(item)
            if announc:
                data.append(announc)
                announc_counter += 1
                
                if announc_counter % FILE_CAPACITY == 0:
                    save_xml(data, files_counter)
                    data = []
                    files_counter += 1

        time.sleep(2)

    if data:
        save_xml(data, files_counter)

        print(f"Парсинг завершён. Всего объявлений: {announc_counter}")