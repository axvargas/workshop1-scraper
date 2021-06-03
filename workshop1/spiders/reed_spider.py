from scrapy.item import Field, Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy.linkextractors import LinkExtractor
# from scrapy.crawler import CrawlerProcess

from itemloaders import ItemLoader
from ..processor_functions import cleanText

# * XPATHS
# ? XPATH FROM SEARCH PAGE
DIV_JOBS_XPATH = '//article'

# ? XPATH FROM INDIVIDUAL JOB PAGE
ID_XPATH              = '//p[@class="reference "]/text()'
TITLE_XPATH           = '//header[contains(@class,"job-header")]//h1/text()'
EMPLOYER_XPATH        = '//span[@itemprop="name"]/text()'
POSTING_DATE_XPATH    = '//span[@itemprop="hiringOrganization"]/text()'
SALARY_XPATH          = '//span[@data-qa="salaryLbl"]/text()'
REGION_XPATH          = '//span[@data-qa="regionLbl"]/text()'
LOCALITY_XPATH        = '//span[@data-qa="localityLbl"]/text()'
EMPLOYMENT_TYPE_XPATH = '//span[@data-qa="jobTypeLbl"]/text()'
REQUIRED_SKILLS_XPATH = '//ul[@class="list-unstyled skills-list"]/li/text()'

# No siempre están
MODALITY_XPATH = '//div[@class="hidden-xs"]/div[@class="metadata container container-max-width-modifier"]/div[4]/text()'

# TODO:
# 4. Assign them to the item
# 5. Clean the data with intput/output_processor
# What happen with empty fields?

# * 1 Define abstraction of your items


class Job(Item):
    id              = Field()
    title           = Field()
    employer        = Field()
    posting_date    = Field()
    salary          = Field()
    region          = Field()
    locality        = Field()
    employment_type = Field()
    modality        = Field()
    required_skills = Field()  # Leave it as array?


# * 2 Define the CrawlSpider

class ReedUKCrawlSpider(CrawlSpider):
    #  * 3 Configuration (headers, limitations, etc)
    name = "reed_uk"

    custom_settings = {
        'USER_AGENT': 'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18',
        'FEEDS': {
            'reed_uk.json': {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True, #Esto es para que se limpie el output.json?
                'fields': ['id', 'title', 'employer', 'posting_date', 'salary',
                           'region', 'locality', 'employment_type','modality', 
                           'required_skills'],
            }
        }
    }

    download_delay = 2

    allowed_domains = ['www.reed.co.uk']

    # * 4 Define the seed urls
    start_urls = [
        'https://www.reed.co.uk/jobs/data-scientist-jobs-in-london']

    # * 5 Define the rules
    rules = (
        # * Horizontal pagination
        Rule(
            LinkExtractor(
                allow=r'/jobs/data-scientist-jobs-in-london\?pageno=\d+$' 
            ), follow=True,
        ),
        # * Vertical pagination
        Rule(
            LinkExtractor(
                allow=r'/jobs/data-scientist/\d+',
                restrict_xpaths=[DIV_JOBS_XPATH]
            ), follow=True, callback='parse_job'
        )
    )

    def parse_job(self, response):
        sel = Selector(response)
        item = ItemLoader(Job(), sel)
        item.add_xpath('id', ID_XPATH)
        item.add_xpath('title', TITLE_XPATH)
        item.add_xpath('employer', EMPLOYER_XPATH)
        item.add_xpath('posting_date', POSTING_DATE_XPATH)
        item.add_xpath('salary', SALARY_XPATH)
        item.add_xpath('region', REGION_XPATH)
        item.add_xpath('locality', LOCALITY_XPATH)
        item.add_xpath('employment_type', EMPLOYMENT_TYPE_XPATH)
        item.add_xpath('required_skills', REQUIRED_SKILLS_XPATH)
        item.add_xpath('modality', MODALITY_XPATH)




        # # TODO: Manage the location (kinda difficult)
        # item.add_value('location', "London")

        # item.add_xpath('salary', SALARY_XPATH)
        # item.add_xpath('job_type', JOB_TYPE_XPATH)
        # item.add_xpath('company', COMPANY_XPATH)
        # item.add_xpath('date_posted', DATE_POSTED_XPATH)

        yield item.load_item()


def cleanText(text):
    return text.replace('\n', '').replace('\r', '').replace('\t', '').strip()

# * RUN SCRAPY PROCCESS
# process = CrawlerProcess()
# process.crawl(ReedUKCrawlSpider)
# process.start()
