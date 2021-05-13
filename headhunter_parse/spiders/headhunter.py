import scrapy
from ..loaders import HhVacancyLoader, HhCompanyLoader
from .. import xpath_selectors


class HeadhunterSpider(scrapy.Spider):
    name = 'headhunter'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    _xpath_selectors = xpath_selectors.xpath_main_selectors

    _xpath_vacancy_selectors = xpath_selectors.xpath_vacancy_selectors

    _xpath_company_selectors = xpath_selectors.xpath_company_selectors

    @staticmethod
    def _get_next(response, selector, callback):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback)

    @staticmethod
    def _create_loader(response, loader_class, loader_xpath_selectors, title):
        loader = loader_class(response=response)
        loader.add_value('url', response.url)
        loader.add_value(*title)
        for xpath_item in loader_xpath_selectors:
            loader.add_xpath(**xpath_item)
        yield loader.load_item()

    def parse(self, response, *args, **kwargs):
        yield from self._get_next(response, self._xpath_selectors['pagination'], self.parse)
        yield from self._get_next(response, self._xpath_selectors['vacancy'], self.parse_vacancy)

    def parse_company(self, response, company_name):
        yield from self._create_loader(response, HhCompanyLoader, self._xpath_company_selectors, company_name)
        yield response.follow(f'{self.start_urls[0]}&employer_id={response.url.split("/")[-1]}',
                              callback=self.parse)

    def parse_vacancy(self, response):
        company_name = ('company_name', response.xpath(self._xpath_selectors['company_name']).getall())
        title = ('title', response.xpath(self._xpath_selectors['vacancy_title']).get())
        yield from self._create_loader(response, HhVacancyLoader, self._xpath_vacancy_selectors, title)
        yield response.follow(response.xpath(self._xpath_vacancy_selectors[-1].get('xpath')).get(),
                              callback=self.parse_company,
                              cb_kwargs={'company_name': company_name})
