# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HeadhunterVacancyItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    company_url = scrapy.Field()


class HeadhunterCompanyItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    company_name = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
    activity_areas = scrapy.Field()
