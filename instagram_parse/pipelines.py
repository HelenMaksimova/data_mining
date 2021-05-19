# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from . import settings
from pymongo import MongoClient
from .items import InstMediaItem


class InstMongoPipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client[settings.BOT_NAME]

    def process_item(self, item, spider):
        collection = f'{spider.name}_media' if isinstance(item, InstMediaItem) \
            else f'{spider.name}_tags'
        self.db[collection].insert_one(item)
        return item


class InstImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for image in item.get("images", []):
            yield Request(image)

    def item_completed(self, results, item, info):
        if item.get("images"):
            item["images"] = [{'path': itm[1]['path'], 'url': itm[1]['url']} for itm in results]
        return item
