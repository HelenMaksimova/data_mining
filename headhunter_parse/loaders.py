from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
from .items import HeadhunterVacancyItem, HeadhunterCompanyItem


def text_clear(text_block):
    text_block = text_block.replace(r'\xa0', ' ').strip()
    return text_block


def description_clear(text):
    text_list = [text_block for text_block in map(lambda x: x.strip(' \n'), text.split('\n')) if not text_block == '']
    return '\n'.join(text_list)


def description_join(text_list):
    return '\n'.join([text_block for text_block in text_list if not text_block == ''])


def company_url_join(url):
    url = urljoin('https://hh.ru/', url)
    return url


def activity_areas_list(areas):
    return [area.strip() for area in ','.join(areas).split(',')]


class HhVacancyLoader(ItemLoader):
    default_item_class = HeadhunterVacancyItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_in = MapCompose(text_clear)
    salary_out = Join()
    description_in = MapCompose(description_clear)
    description_out = description_join
    company_url_in = MapCompose(company_url_join)
    company_url_out = TakeFirst()


class HhCompanyLoader(ItemLoader):
    default_item_class = HeadhunterCompanyItem
    url_out = TakeFirst()
    company_name_in = MapCompose(text_clear)
    company_name_out = Join()
    description_in = MapCompose(description_clear)
    description_out = description_join
    link_out = TakeFirst()
    activity_areas_out = activity_areas_list

