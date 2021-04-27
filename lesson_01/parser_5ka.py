import requests
import pathlib
import json
import urllib.parse as url_prs
import time
from collections import namedtuple

# Решила действовать следующим образом:
# 1. Вытащить список кодов и названий категорий. Для хранения результатов использовала генератор и namedtuple
# (по какому url лежат данные по категориям выяснила через инстуметны разработчика в браузере).
# 2. В методе run пробежаться по всем кодам категорий и сделать запросы на соответсвующие страницы
# (какой параметр указывать выяснила опытным путём, способ отправки GET-запросов знаю из вебинара)
# 3. Сформировать список словарей с продуктами. Не забыть про пагинацию -
# например, создать пустой список и добавлять в него значения с каждой страницы в одной категории.
# Как избежать проблем с заменой домена знаю из вебинара, сделала так же.
# 4. Если в итоге список словарей продуктов не пустой, то сформировать итоговый стоварь по категории
# и отправить его на сохранение


class Parser5ka:
    """
    Parser for parsing '5ka'-shop's site
    """

    response_time = 0
    delay = 1
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'}

    def __init__(self, base_url, save_dir):
        self.base_url = base_url
        self.save_dir = save_dir

    def get_categories(self):
        CATEGORY_INFO = namedtuple('Category_info', 'code, name')
        url = self.base_url.replace('special_offers', 'categories')
        categories_gen = (CATEGORY_INFO(category['parent_group_code'], category['parent_group_name'])
                          for category in json.loads(self.get_response(url).content))
        return categories_gen

    def run(self):
        for category in self.get_categories():
            url = url_prs.urljoin(self.base_url, f'?categories={category.code}')
            products_list = list()
            while True:
                products_dict = json.loads(self.get_response(url).content)
                products_list.extend(products_dict['results'])
                if products_dict['next'] is None:
                    break
                url = products_dict['next']
                url = url.replace(url_prs.urlparse(url).netloc, url_prs.urlparse(self.base_url).netloc)
            if products_list:
                category_dict = {
                    "name": category.name,
                    "code": category.code,
                    "products": products_list
                }
                self.save_data(category_dict)

    def get_response(self, url):
        next_time = self.response_time + self.delay
        while True:
            now_time = time.time()
            if next_time > now_time:
                time.sleep(next_time - now_time)
            response = requests.get(url, headers=self.headers)
            self.response_time = time.time()
            if 200 <= response.status_code < 300:
                return response
            time.sleep(self.delay)

    def save_data(self, data):
        file_name = f'{data.get("code")}.json'
        data_path = self.save_dir.joinpath(file_name)
        data_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')


def result_dir(dir_name):
    result_path = pathlib.Path(__file__).parent.joinpath(dir_name)
    if not result_path.exists():
        result_path.mkdir()
    return result_path


if __name__ == '__main__':
    path = result_dir('products_with_categories')
    parser = Parser5ka('https://5ka.ru/api/v2/special_offers/', path)
    parser.run()
