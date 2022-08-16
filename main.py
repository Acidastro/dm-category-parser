import csv
import datetime
import json
import random
from time import sleep

from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, ChromeOptions


def get_data(url: str):
    # Заходит на сайт, считывает нужный блок данных, и возвращает его в формате json
    options = ChromeOptions()
    options.headless = True
    browser = Chrome(options=options)
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, 'lxml')
    data = (soup.find('pre').text.strip())
    return json.loads(data)


def get_amount(name_category: str):
    # Узнать количество товаров в категории
    url = f'https://api.detmir.ru/v2/products?filter=categories[].alias:{name_category};withregion:RU-MOW&meta=*'
    data_dict = get_data(url)
    length = data_dict['meta']['length']
    print(f'Количество товаров в категории: {length}')
    return length


def get_category(url: str):
    # Имя категории: https://www.detmir.ru/catalog/index/name/pups/ = 'pups'
    """
    :param url: url to get data from
    :return: Name category or False
    """
    tmp = url.find('index/name/')
    if tmp > 0:
        len_tmp = len('index/name/')
        name_category = url[tmp + len_tmp:]
        if name_category[-1] == '/':
            name_category = name_category[:-1]
        return name_category
    else:
        print('Категория не найдена, введите верный URL')
        return False


def read_and_write(url: str, city: str):
    # Обрабатывает данные с сайта, выбирает нужные и добавляет их в result_list
    result_list = []
    data_dict = get_data(url)
    for card in data_dict:
        card_id = card['id']
        title = card['title']
        price = card['price']['price']
        try:
            promo_price = card['old_price']['price']
        except TypeError:
            promo_price = ''
        url = card['link']['web_url']
        result_list.append((card_id, title, price, promo_price, url, city))
    sleep(random.randrange(2, 5))
    return result_list


def collect_data(url: str):
    # Берет данные по 100шт, и добавляет в единый список с дальнейшей записью в csv
    # Api имеет лимит отдачи в 100 позиций, offset смещает позицию
    if get_category(url):
        name_category = get_category(url)
        print('Категория', name_category)
    else:
        raise ValueError('Неверный URL')

    length = get_amount(name_category)  # Количество карточек в категории
    result_list = []
    for offset in range(0, length, 100):
        url_spb = f'https://api.detmir.ru/v2/products?filter=categories[].alias:{name_category}' \
                  f';withregion:RU-SPE&limit=100&offset={offset}'
        url_msk = f'https://api.detmir.ru/v2/products?filter=categories[].alias:{name_category}' \
                  f';withregion:RU-MOW&limit=100&offset={offset}'
        result_list += read_and_write(url_spb, 'SPB')
        result_list += read_and_write(url_msk, 'MOSCOW')
        print(offset, 'offset ok')
    time = datetime.datetime.now().strftime("%d_%m_%H_%M")
    with open(f'result_{name_category}-{time}.csv', 'w', newline='', encoding='UTF-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            ('id',
             'title',
             'price',
             'promo_price',
             'url',
             'city')
        )
        writer.writerows(result_list)


def main():
    url = 'https://www.detmir.ru/catalog/index/name/pups/'  # Вставить сюда url
    collect_data(url)


if __name__ == '__main__':
    main()
