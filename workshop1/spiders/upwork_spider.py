from scrapy.item import Field, Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy.linkextractors import LinkExtractor
# from scrapy.crawler import CrawlerProcess

from itemloaders import ItemLoader
from ..processor_functions import cleanText

# * XPATHS
DIV_JOBS_XPATH = '//section[@data-ng-repeat-start]'
# ID_XPATH = './/h3/a/@data-id'
TITLE_XPATH = './/h4/a/text()'
# LOCATION_XPATH_A = './/div[@class="detail-body"]//li[@class="location"]/span/a/text()'
# LOCATION_XPATH_SPAN = './/div[@class="detail-body"]//li[@class="location"]/span/span/text()'
# SALARY_XPATH = './/div[@class="detail-body"]//li[@class="salary"]/text()'
# JOB_TYPE_XPATH = './/div[@class="detail-body"]//li[@class="job-type"]/span/text()'
# COMPANY_XPATH = './/div[@class="detail-body"]//li[@class="company"]//a/text()'
# DATE_POSTED_XPATH = './/div[@class="detail-body"]//li[@class="date-posted"]/span/text()'

# * 1 Define abstraction of your items


class Job(Item):
    # id = Field()
    title = Field()
    # location = Field()
    # salary = Field()
    # job_type = Field()
    # company = Field()
    # date_posted = Field(
    #     input_processor=MapCompose(cleanText)
    # )


# * 2 Define the CrawlSpider

class UpworkCrawlSpider(CrawlSpider):
    #  * 3 Configuration (headers, limitations, etc)
    name = "upwork"

    custom_settings = {
        'USER_AGENT': 'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18',
        'FEEDS': {
            'upwork.json': {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True,
                'fields': ['title'],
                # 'salary', 'job_type', 'company', 'date_posted'
            }
        }
    }

    download_delay = 2

    allowed_domains = ['www.upwork.com']

    # * 4 Define the seed urls
    start_urls = [
        'https://www.upwork.com/search/jobs/?q=Data%20science%20UK&sort=recency']

    # * 5 Define the rules
    rules = (
        # * Horizontal pagination
        Rule(
            LinkExtractor(
                allow=r'page=\d+'  # ! \d+ means that any number will be there
            ), follow=True, callback='parse_job'
        ),
    )

    def parse_job(self, response):
        sel = Selector(response)
        div_jobs = sel.xpath(DIV_JOBS_XPATH)

        for div in div_jobs:
            item = ItemLoader(Job(), div)
            # item.add_xpath('id', ID_XPATH)
            item.add_xpath('title', TITLE_XPATH)

            # # TODO: Manage the location (kinda difficult)
            # item.add_value('location', "London")

            # item.add_xpath('salary', SALARY_XPATH)
            # item.add_xpath('job_type', JOB_TYPE_XPATH)
            # item.add_xpath('company', COMPANY_XPATH)
            # item.add_xpath('date_posted', DATE_POSTED_XPATH)

            yield item.load_item()


# * RUN SCRAPY PROCCESS
# process = CrawlerProcess()
# process.crawl(UpworkCrawlSpider)
# process.start()
