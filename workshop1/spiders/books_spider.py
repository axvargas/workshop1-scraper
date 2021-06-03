from scrapy import Item, Field
from scrapy.selector import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from scrapy.crawler import CrawlerProcess
from scrapy.loader.processors import MapCompose, TakeFirst

from itemloaders import ItemLoader

# * XPATHS
TITLE_XPATH = '//div[contains(@class,"product_main")]/h1/text()'
TAX_XPATH = '//table//th[text()="Tax"]/following-sibling::td/text()'
PRICE_XPATH = '//table//th[text()="Price (incl. tax)"]/following-sibling::td/text()'
AVAILABLE_BOOKS_XPATH = '//table//th[text()="Availability"]/following-sibling::td/text()'


def cleanText(laString):
    res = [int(i) for i in laString.replace('(', '').split() if i.isdigit()]
    return res


class BookItem(Item):
    title = Field(
        output_processor=TakeFirst()
    )
    tax = Field(
        output_processor=TakeFirst()
    )
    price = Field(
        output_processor=TakeFirst()
    )
    availability = Field(
        input_processor=MapCompose(cleanText),
        output_processor=TakeFirst()
    )


class CrawlerTaller(CrawlSpider):
    """
    This CrawlSpider will get information about books. It will navigate through the links of the page
    """
    name = 'books'
    allowed_domains = ['books.toscrape.com']

    custom_settings = {
        'USER_AGENT': 'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18',
        'FEEDS': {
            'books.json': {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True,
                'fields': ['title', 'tax', 'price', 'availability'],
            }
        },
        'CLOSESPIDER_ITEMCOUNT': '5'
    }

    start_urls = ['https://books.toscrape.com/']

    rules = [
        Rule(
            LxmlLinkExtractor(
                allow=r'/sequential-art',
                restrict_xpaths=[
                    '//ul[@class="nav nav-list"]/li/ul/li/a[contains(@href, "sequential")]']
            ), follow=True
        ),
        # ! Rule for next page
        Rule(
            LxmlLinkExtractor(
                allow=r'/page-\d+',
            ), follow=True,
        ),
        # * Extract the data
        Rule(
            LxmlLinkExtractor(
                allow=r'/catalogue/',
                restrict_xpaths=[
                    '//ol[@class="row"]/li//div[@class="image_container"]/a']
            ), follow=True, callback='parse_books' #follow es para que de click
        ),
    ]

    def parse_books(self, response):
        """
        This function takes the information from each page and return the items in the catalog.
        """
        self.logger.info('Now we are crawling: %s', response.url)
        sel = Selector(response)
        item = ItemLoader(BookItem(), sel)
        item.add_xpath('title', TITLE_XPATH)
        item.add_xpath('tax', TAX_XPATH)
        item.add_xpath('price', PRICE_XPATH)
        item.add_xpath('availability', AVAILABLE_BOOKS_XPATH)

        # ....
        yield item.load_item()

# ! TO RUN THE CODE USE $ scrapy crawl <name_of_crawlerspider>

# process = CrawlerProcess(
#     settings={
#         'FEED_FORMAT': ...,
#         'FEED_URI': ...,
#         # Close spider after number of crawled page responses have been requested
#         # 'CLOSESPIDER_ITEMCOUNT' : '5'
#     }
# )
# process.crawl(...)
# process.start()
