import scrapy
import pymongo
import re
from urllib.parse import urljoin


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    client = pymongo.MongoClient('mongodb://localhost:27017')
    db = client['autoyoula_parse']
    collection = db['parse_cars']

    records_count = 0

    def _get_follow(self, response, selector, callback):
        for link in response.css(selector):
            url = link.attrib["href"]
            yield response.follow(url, callback=callback)

    def parse(self, response):
        yield from self._get_follow(
            response,
            "div.TransportMainFilters_brandsList__2tIkv .ColumnItemList_column__5gjdt a.blackLink",
            self.brand_parse,
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response, "div.Paginator_block__2XAPy a.Paginator_button__u1e7D", self.brand_parse,
        )
        yield from self._get_follow(
            response,
            "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu",
            self.car_parse,
        )

    def car_parse(self, response):
        data = {
            "url": response.url,
            "title": response.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first(),
            "description": response.css(".AdvertCard_descriptionInner__KnuRi::text").extract_first(),
            "characteristics": self.characteristics_parse(response),
            "seller_url": self.seller_parse(response),
            "images": self.images_parse(response)
        }
        yield self.save_data(data)

    @staticmethod
    def seller_parse(response):
        # Нужную информацию о продавце смогла найти только в скриптах на странице. Вытащила регулярками.
        # В процессе выяснилось, что объявления размещают не только пользователи, но ещё и организации (автосалоны),
        # поэтому пришлось проверять сперва нет ли информации об автосалоне, а затем уже о пользователе.
        scripts_list = response.css('script::text').getall()
        pattern_seller = r'cardealers%2F(.*?)%2F%23info'
        pattern_user = r'youlaId%22%2C%22(\w*?)%22%2C%22avatar'
        for script in scripts_list:
            temp_seller = re.findall(pattern_seller, script)
            if temp_seller:
                return urljoin('https://auto.youla.ru/cardealers/', temp_seller[0])
            temp_user = re.findall(pattern_user, script)
            if temp_user:
                return urljoin('https://youla.ru/user/', temp_user[0])

    @staticmethod
    def characteristics_parse(response):
        # берём каждый блок с нужным классом, из подблоков вытаскиваем название характеристики и её значение,
        # пишем в словарь. В некоторых характеристиках нужный текст содержится в ссылке внутри блока.
        # Поэтому сначала проверяем текст ссылки, если ссылки в блоке нет, проверяем текст родительского блока
        characteristics = dict()
        for element in response.css('.AdvertSpecs_row__ljPcX'):
            value = element.css('.AdvertSpecs_data__xK2Qx a::text').get()
            if not value:
                value = element.css('.AdvertSpecs_data__xK2Qx::text').get()
            characteristics[element.css('.AdvertSpecs_label__2JHnS::text').get()] = value
        return characteristics

    @staticmethod
    def images_parse(response):
        # На странице отображается только 6 картинок, в то время как их на самом деле может быть гораздо больше.
        # Нашла ссылки на все картинки в одном из скриптов на странице, поэтому парсила из скриптов.
        scripts_list = response.css('script::text').getall()
        pattern_image = r'automobile_m3%2F(document)%2F(.*?)%2F(.*?)%2F(.*?)%2F(.*?\.jpg)'
        for script in scripts_list:
            temp_images = re.findall(pattern_image, script)
            if temp_images:
                links_images = [urljoin('https://static.am/automobile_m3/', '/'.join(link))
                                for link in temp_images
                                if 'l' in link]
                return links_images

    def save_data(self, data):
        self.collection.insert_one(data)
        self.records_count += 1
        print(f'{self.records_count} record is done')
