from scrapy.item import Item, Field


class LivingSocialDeal(Item):
    '''LivingSocial container (dict-like) for scraping data.'''
    title = Field()
    link = Field()
    location = Field()
    original_price = Field()
    price = Field()
    end_date = Field()
