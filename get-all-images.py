import scrapy
import pprint
from scrapy.spiders import SitemapSpider

class ExampleItem(scrapy.Item):
    url = scrapy.Field()
    images = scrapy.Field()

class Coolspider(SitemapSpider):
    name = "whatapDocs"
    sitemap_urls = [ "https://docs.whatap.io/sitemap.xml" ]

    def parse(self, response):
        example_item = ExampleItem()
        example_item["url"] = response.url
        example_item["images"] = response.css(".theme-doc-markdown.markdown img").xpath("@src").getall()

        return example_item
