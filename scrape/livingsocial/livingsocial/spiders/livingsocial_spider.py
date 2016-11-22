from livingsocial.items import LivingSocialDeal
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, MapCompose
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy.spiders import Spider


class LivingSocialSpider(Spider):
    '''Spider for up-to-date livingsocial.com site, Seattle page.'''
    name = 'livingsocial'
    allowed_domains = ["livingsocial.com"]
    start_urls = ["https://www.livingsocial.com/cities/27-seattle"]
    deals_list_xpath = '//li[@dealid]'
    item_fields = {
        'title': './/a/div[@class="deal-details"]/h2/text()',
        'subtitle': './/a/div[@class="deal-details"]/h3/text()',
        'description': './/a/div[@class="deal-details"]/p[@class="description"]/text()',
        'link': './/a/@href',
        'location': './/a/div[@class="deal-details"]/p[@class="location"]/text()',
        'original_price': './/a/div[@class="deal-prices"]/div[@class="deal-strikethrough-price"]/div[@class="strikethrough-wrapper"]/sup/following-sibling::text()',
        'price': './/a/div[@class="deal-prices"]/div[@class="deal-price"]/text()'
    }

    def parse(self, response):
        '''Default Scrapy callback to process downloaded responses.'''
        selector = Selector(response=response)
        for deal in selector.xpath(self.deals_list_xpath):
            loader = ItemLoader(LivingSocialDeal(), deal)
            loader.default_input_processor = MapCompose(str.strip)
            loader.default_output_processor = Join()
            for field, xpath in self.item_fields.items():
                loader.add_xpath(field, xpath)
            yield loader.load_item()
