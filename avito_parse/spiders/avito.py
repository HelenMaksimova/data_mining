import scrapy
from . import xpath_selectors
from json import loads
from ..loaders import AvitoFlatLoader


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru']
    start_urls = ['https://www.avito.ru/krasnodar/kvartiry/prodam']

    _main_selectors = xpath_selectors.main_selectors
    _flat_selectors = xpath_selectors.flat_selectors

    def parse(self, response, *args, **kwargs):
        page_data = loads(response.xpath(self._main_selectors['js_script_data']).get())
        yield from self.parse_links(page_data, response)

    def parse_links(self, page_data, response):
        for item in page_data['catalog']['items']:
            if item.get('type') == 'item':
                yield response.follow(item.get('urlPath'), callback=self.parse_flat)
            elif item.get('type') == 'vip':
                self.parse_links(item, response)
            elif item.get('type') == 'witcher':
                yield response.follow(item.get('buttonUrl'), callback=self.parse)
        yield response.follow(page_data['catalog']['pager'].get('next'), callback=self.parse)

    def parse_flat(self, response):
        loader = AvitoFlatLoader(response=response)
        loader.add_value('url', response.url)
        for xpath_item in self._flat_selectors:
            loader.add_xpath(**xpath_item)
        yield loader.load_item()
