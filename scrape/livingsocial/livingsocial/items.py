# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LivingSocialDeal(scrapy.Item):
    '''LivingSocial container (dict-like) for scraping data.'''
    title = scrapy.Field()
    subtitle = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
    location = scrapy.Field()
    original_price = scrapy.Field()
    price = scrapy.Field()
