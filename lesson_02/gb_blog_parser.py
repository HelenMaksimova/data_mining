import time
import typing
import json
import requests
from urllib.parse import urljoin, urlparse
import bs4
from collections import deque
import datetime
import pymongo


class GbBlogParse:
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'
    }
    __parse_time = 0

    def __init__(self, stat_url, db_collection, delay=1.0):
        self.start_url = stat_url
        self.db_collection = db_collection
        self.delay = delay
        self.done_urls = set()
        # заменила класс очереди с list на deque
        self.tasks = deque()
        self.task_creator(self.start_url, callback=self.parse_feed)
        self.count = 0

    def _get_response(self, url):
        next_time = self.__parse_time + self.delay
        while True:
            if next_time > time.time():
                time.sleep(next_time - time.time())
            response = requests.get(url, headers=self.headers)
            self.__parse_time = time.time()
            # изменила условие - пару раз парсер зависал из-за получения статуса 206
            if 200 <= response.status_code < 300:
                return response
            else:
                print(response.status_code)
            time.sleep(self.delay)

    def _get_soup(self, url):
        response = self._get_response(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        return soup

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        return task

    def task_creator(self, *urls, callback):
        urls_set = set(urls) - self.done_urls
        for url in urls_set:
            self.tasks.append(self.get_task(url, callback))
            self.done_urls.add(url)

    def parse_feed(self, url, soup):
        ul_pagination = soup.find("ul", attrs={"class": "gb__pagination"})
        pag_links = set(
            urljoin(url, itm.attrs.get("href"))
            for itm in ul_pagination.find_all("a")
            if itm.attrs.get("href")
        )
        self.task_creator(*pag_links, callback=self.parse_feed)
        post_links = set(
            urljoin(url, itm.attrs.get("href"))
            for itm in soup.find_all("a", attrs={"class": "post-item__title"})
            if itm.attrs.get("href")
        )
        self.task_creator(*post_links, callback=self.parse_post)

    def parse_post(self, url, soup):

        domain = urlparse(url).netloc  # для формирования ссылки на страницу автора

        # не во всех постах есть картинки, пришлось добавить проверку
        find_result = soup.find('div', attrs={'class': 'blogpost-content'}).find('img')
        first_img_link = find_result.get('src') if find_result is not None else None

        # блок для получения комментариев (с использованием объекта класса ParseComments)
        comments_id = soup.find('comments')['commentable-id']
        comments_url = f'https://gb.ru/api/v2/comments?commentable_type=Post&commentable_id={comments_id}'
        comments_parse = ParseComments(self._get_response(comments_url))
        comments = comments_parse.run()

        data = {
            "url": url,
            "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
            "first_img_link": first_img_link,
            "post_time": datetime.datetime.strptime(soup.find('time').get('datetime'), '%Y-%m-%dT%H:%M:%S+%I:00'),
            "author_name": soup.find('div', attrs={'itemprop': 'author'}).text,
            "author_link": urljoin(f'https://{domain}',
                                   soup.find('div', attrs={'itemprop': 'author'}).parent.get('href')),
            "comments": comments
        }

        return data

    def run(self):
        # немного переписала цикл без try-except
        while self.tasks:
            task = self.tasks.popleft()
            result = task()
            if isinstance(result, dict):
                self.save(result)

    def save(self, data):
        self.db_collection.insert_one(data)
        self.count += 1
        print(f'{self.count} record is done')


# Для вытаскивания комментариев из вложенной структуры решила воспользоваться изученным на вебинаре методом
# с очередью задач и callback. Чтобы не загромождать код основного парсера, написала отдельный класс
# для парсинга комментариев

class ParseComments:

    def __init__(self, comments_response):
        self.comments_response = comments_response
        self.comments_task = deque()
        self.user_url = comments_response.url

    @staticmethod
    def get_comment_task(comment, callback):
        def comment_task():
            return callback(comment)
        return comment_task

    def get_comments_data(self, comments):
        result = list()
        domain = urlparse(self.user_url).netloc
        for comment in comments:
            comment = comment.get('comment')
            result.append({
                'message': comment.get('body'),
                'author_name': f"{comment['user'].get('first_name')} {comment['user'].get('last_name')}",
                'author_link': urljoin(f'https://{domain}/users/', str(comment['user'].get('id')))
            })
        return result

    def get_comments(self, comments):
        for elem in comments:
            elem = elem.get('comment')
            children = elem.get('children')
            if children:
                self.comments_task.append(self.get_comment_task(children, self.get_comments))
        self.comments_task.append(self.get_comment_task(comments, self.get_comments_data))

    def run(self):
        comments = list()
        comments_list = json.loads(self.comments_response.text)
        self.get_comments(comments_list)
        while self.comments_task:
            task = self.comments_task.popleft()
            result = task()
            if isinstance(result, list):
                comments.extend(result)
        return comments


if __name__ == "__main__":
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
    db = mongo_client["gb_parse_01_05_2021"]
    collection = db["gb_blog_parse"]
    parser = GbBlogParse("https://gb.ru/posts", collection, delay=0.1)
    parser.run()
