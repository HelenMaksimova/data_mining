from .items import AvitoFlatItem
from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose


def clear_characteristics(char_list):
    cleared_list = [elem for elem in map(lambda x: x.strip(' \n:'), char_list) if not elem == '']
    if cleared_list:
        result = {item[0]: item[1] for item in zip(cleared_list[0::2], cleared_list[1::2])}
        return result


def clear_price(price):
    price = float(price.replace(' ', ''))
    return price


def url_join(url):
    return urljoin('https://www.avito.ru', url)


class AvitoFlatLoader(ItemLoader):
    default_item_class = AvitoFlatItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_in = MapCompose(clear_price)
    price_out = TakeFirst()
    characteristics_out = clear_characteristics
    seller_url_in = MapCompose(url_join)
    seller_url_out = TakeFirst()
    address_in = MapCompose(lambda x: x.strip(' \n'))
    address_out = TakeFirst()
