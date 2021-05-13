# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from . import settings
from .items import HeadhunterVacancyItem
from pymongo import MongoClient


class GbMongoPipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client[settings.BOT_NAME]

    def process_item(self, item, spider):
        collection = f'{spider.name}_vacancies' if isinstance(item, HeadhunterVacancyItem) \
            else f'{spider.name}_companies'
        self.db[collection].insert_one(item)
        return item
