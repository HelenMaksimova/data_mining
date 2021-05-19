import scrapy
import json
from ..loaders import InstMediaLoader, InstTagLoader
import datetime


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com"]
    start_urls = ["https://www.instagram.com/"]
    _login_url = "https://www.instagram.com/accounts/login/ajax/"
    _tags_path = "/explore/tags/"

    def __init__(self, login, password, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.tags = tags
        self.auth_flag = False
        self.media_count = 10

    def authorization(self, response):
        js_data = self.js_data_extract(response)
        self.auth_flag = True
        yield scrapy.FormRequest(
            self._login_url,
            method="POST",
            callback=self.parse,
            formdata={"username": self.login, "enc_password": self.password},
            headers={"X-CSRFToken": js_data["config"]["csrf_token"]},
        )

    def parse(self, response, *args, **kwargs):
        if not self.auth_flag:
            yield from self.authorization(response)
        else:
            for tag in self.tags:
                url = f"{self._tags_path}{tag}/"
                yield response.follow(url, callback=self.tag_page_parse, cb_kwargs={'tag_name': tag})

    def tag_page_parse(self, response, tag_name):
        media_data = self.get_data(response)
        end_cursor = media_data['edge_hashtag_to_media']['page_info'].get('end_cursor')
        next_url = self.get_next_url(tag_name, end_cursor)
        if isinstance(response, scrapy.http.HtmlResponse):
            tag_info_data = {'url': response.url, 'id': media_data['id'], 'name': media_data['name']}
            yield from self.item_load(tag_info_data, InstTagLoader)
        for media_item in media_data['edge_hashtag_to_media']['edges']:
            yield from self.item_load(media_item['node'], InstMediaLoader)
        yield response.follow(next_url, callback=self.tag_page_parse, cb_kwargs={'tag_name': tag_name})

    def get_data(self, response):
        if isinstance(response, scrapy.http.HtmlResponse):
            js_data = self.js_data_extract(response)
            return js_data['entry_data']['TagPage'][0]['graphql']['hashtag']
        else:
            js_data = response.json()
            return js_data['data']['hashtag']

    def get_next_url(self, tag_name, end_cursor):
        return f'https://www.instagram.com/graphql/query/?query_hash=9b498c08113f1e09617a1703c22b2f32' \
               f'&variables={"{"}"tag_name":"{tag_name}","first":{self.media_count},"after":"{end_cursor}"{"}"}'

    @staticmethod
    def item_load(item, loader_class):
        loader = loader_class()
        loader.add_value('date_parse', datetime.datetime.now())
        loader.add_value('data', item)
        if loader_class == InstMediaLoader:
            loader.add_value('images', [itm.get('src') for itm in item['thumbnail_resources']])
        yield loader.load_item()

    @staticmethod
    def js_data_extract(response):
        script = response.xpath(
            "//script[contains(text(), 'window._sharedData = ')]/text()"
        ).extract_first()
        return json.loads(script.replace("window._sharedData = ", "")[:-1])
