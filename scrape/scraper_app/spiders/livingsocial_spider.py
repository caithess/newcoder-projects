from scrapy import BaseSpider

from scraper_app.items import LivingSocialDeal


class LivingSocialSpider(BaseSpider):
    '''Spider for up-to-date livingsocial.com site, Seattle page.'''
    name = 'livingsocial'
    allowed_domains =

