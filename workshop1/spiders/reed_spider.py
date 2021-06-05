from scrapy.item import Field, Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.downloadermiddlewares.retry import RetryMiddleware

from itemloaders.processors import MapCompose, TakeFirst
from itemloaders import ItemLoader
from ..processor_functions import cleanText, clean_posting_date, clean_id

# * XPATHS
# ? XPATH FROM SEARCH PAGE
DIV_JOBS_XPATH = '//article'

# ? XPATH FROM INDIVIDUAL JOB PAGE
ID_XPATH                = '//p[@class="reference "]/text()'
TITLE_XPATH             = '//header[contains(@class,"job-header")]//h1/text()'
ALTERNATIVE_TITLE_XPATH = '//div[contains(@class,"job-header")]//h1/text()'
EMPLOYER_XPATH          = '//span[@itemprop="name"]/text()'
POSTING_DATE_XPATH      = '//span[@itemprop="hiringOrganization"]/text()'
SALARY_XPATH            = '//meta[@itemprop="currency"]/following-sibling::span[1]/text()'
COUNTRY_XPATH           = '//span[@id="jobCountry"]/@value'
REGION_XPATH            = '//meta[@itemprop="addressRegion"]/@content'
LOCALITY_XPATH          = '//span[@itemprop="addressLocality"]/text()'
EMPLOYMENT_TYPE_XPATH   = '//span[@itemprop="employmentType"]/text()'
REQUIRED_SKILLS_XPATH   = '//ul[@class="list-unstyled skills-list"]/li/text()'
IS_REMOTE_XPATH         = '//i[contains(@class,"remote")]'
BE_IN_FIRST_TEN_XPATH   = '//i[contains(@class,"applicants")]'


# * 1 Job abraction gets defined
class Job(Item):
    """Class that models the job posting items extracted from the webpage reed.co.uk"""
    id = Field(
        input_processor=MapCompose(cleanText, clean_id),
        output_processor=TakeFirst()
    )
    title = Field(
        input_processor=MapCompose(cleanText),
        output_processor=TakeFirst()
    )
    employer = Field(
        input_processor=MapCompose(cleanText),
        output_processor=TakeFirst()
    )
    posting_date = Field(
        input_processor=MapCompose(cleanText, clean_posting_date),
        output_processor=TakeFirst()
    )
    salary = Field(
        input_processor=MapCompose(cleanText),
        output_processor=TakeFirst()
    )
    country = Field(
        input_processor=MapCompose(cleanText),
        output_processor=TakeFirst()
    )
    region = Field(
        input_processor=MapCompose(cleanText),
        output_processor=TakeFirst()
    )
    locality = Field(
        input_processor=MapCompose(cleanText),
        output_processor=TakeFirst()
    )
    employment_type = Field(
        input_processor=MapCompose(cleanText),
        output_processor=TakeFirst()
    )
    required_skills = Field(
        input_processor=MapCompose(cleanText),
    )
    is_remote = Field(
        output_processor=TakeFirst()
    )
    be_in_first_ten = Field(
        output_processor=TakeFirst()
    )


# * 2 Define the CrawlSpider

class ReedUKCrawlSpider(CrawlSpider):
    """
    Class that inherits from CrawlerSpider, which contains all the functionality
    of the Crawler to extract the data
    """


    #  * 3 Configuration (headers, files, limitations, etc)
    name = "reed_uk"

    custom_settings = {
        'USER_AGENT': 'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18',
        'FEEDS': {
            'reed_uk.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'overwrite': True,
                'fields': ['id', 'title', 'employer', 'posting_date',
                           'salary', 'country', 'region', 'locality',
                           'employment_type', 'is_remote', 'be_in_first_ten',
                           'required_skills']
            }
        },
        'CONCURRENT_REQUESTS': 32,
        'ROBOTSTXT_OBEY': True,
        # ! To handle time between requirements
        'DOWNLOAD_DELAY': 1,
        # ! To handle connection errors
        'DOWNLOADER_MIDDLEWARES': {
            "scrapy.downloadermiddlewares.retry.RetryMiddleware": 500
        },
        'RETRY_HTTP_CODES': [
            500, 502, 503, 504, 522, 524, 400, 408, 429, 403],
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 10,
    }

    allowed_domains = ['www.reed.co.uk']

    # * 4 Define the seed urls
    start_urls = ['https://www.reed.co.uk/jobs/data-scientist-jobs']

    # * 5 Define the rules
    rules = (
        # * Horizontal pagination
        Rule(
            LinkExtractor(
                allow=r'/jobs/data-scientist-jobs\?pageno=\d+$'
            ), follow=True,
        ),
        # * Vertical pagination
        Rule(
            LinkExtractor(
                allow=r'/jobs/.*/\d+',
                restrict_xpaths=[DIV_JOBS_XPATH],
            ), follow=True, callback='parse_job'
        )
    )

    def parse_job(self, response):
        """
        Function that obtain all the data once the crawler reched the desired url
        given by the rules of the SpiderCrawler
        """


        sel = Selector(response)
        item = ItemLoader(Job(), sel)
        item.add_xpath('id', ID_XPATH)
        item.add_xpath('employer', EMPLOYER_XPATH)
        item.add_xpath('posting_date', POSTING_DATE_XPATH)
        item.add_xpath('salary', SALARY_XPATH)
        item.add_xpath('region', REGION_XPATH)
        item.add_xpath('locality', LOCALITY_XPATH)
        item.add_xpath('employment_type', EMPLOYMENT_TYPE_XPATH)
        item.add_xpath('required_skills', REQUIRED_SKILLS_XPATH)
        item.add_xpath('country', COUNTRY_XPATH)

        title = sel.xpath(TITLE_XPATH).get()
        if not title:
            title = sel.xpath(ALTERNATIVE_TITLE_XPATH).get()
        item.add_value('title', title)

        has_remote_work = sel.xpath(IS_REMOTE_XPATH)
        if has_remote_work:
            item.add_value('is_remote', True)
        else:
            item.add_value('is_remote', False)

        has_to_be_in_first_ten = sel.xpath(BE_IN_FIRST_TEN_XPATH)
        if has_to_be_in_first_ten:
            item.add_value('be_in_first_ten', True)
        else:
            item.add_value('be_in_first_ten', False)

        yield item.load_item()
