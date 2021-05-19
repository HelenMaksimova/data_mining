from .items import InstTagItem, InstMediaItem
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst


class InstMediaLoader(ItemLoader):
    default_item_class = InstMediaItem
    date_parse_out = TakeFirst()
    data_out = TakeFirst()


class InstTagLoader(ItemLoader):
    default_item_class = InstTagItem
    date_parse_out = TakeFirst()
    data_out = TakeFirst()
