import json
import scrapy
import re
from scrapy.spiders import SitemapSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

class ExampleItem(scrapy.Item):
    url = scrapy.Field()
    description = scrapy.Field()
    product = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()

class Coolspider(SitemapSpider):
    name = "whatapDocs"
    sitemap_urls = [ "https://docs.whatap.io/sitemap.xml" ]

    def parse_options(self, response):
        example_item = ExampleItem()
        example_item["url"] = response.url
        example_item["description"] = response.xpath("//*/head/meta[@name='description']/@content").get()
        example_item["product"] = response.xpath(
            "//*/nav[contains(@class, 'theme-doc-breadcrumbs')]/ul/li[2]//span/text() | //*/nav[contains(@class,'menu')]/ul/li[1]//a/text()").get()
        example_item["title"] = response.css("header h1::text").get()
        sections = response.xpath("//*/div[contains(@class, 'theme-doc-markdown')]")
        # contents = []

        for section in sections:
            # section_title = section.xpath(".//h2/text()").get()
            # section_text = section.xpath(".//p/text()").get()
            options = section.xpath(".//li")
            options_list = []

            for option in options:
                # str 타입인지 확인한다.
                if (type(option.xpath(".//p[2]/text()").get()) == str):
                    if option.xpath(".//p[2]/text()").get().startswith("기본값"):
                        default_val = option.xpath(".//p[2]/code/text()").get()
                        default_check = True
                    else:
                        default_val = "Empty"
                        default_check = False

                    if default_check is True:
                        desc_string = ''.join(option.xpath("string(.//p[3])").extract()).strip()
                    else:
                        desc_string = ''.join(option.xpath("string(.//p[2])").extract()).strip()

                    option_name = option.xpath("./p[1]/strong/text()").get()
                    option_type = option.xpath("./p[1]/span[@class='type']/text() | ./p[1]/span[@class='api']/text()").get()

                    if option_name is not None:
                        option_data = {
                            "name": option_name,
                            "type": option_type,
                            "default": default_val,
                            "description": desc_string.replace(str(option_name), '').replace(str(option_type), '').replace(default_val, '').replace('기본값', '').strip()
                            # "example": option.xpath(".//pre/code/text()").get()
                        }
                        options_list.append(option_data)
                else:
                    pass

            content_data = {
                "agent_options": options_list
            }
            contents = json.dumps(options_list, ensure_ascii=False)
            # contents.append(content_data)

        example_item["contents"] = contents
        return example_item


    def parse(self, response):
        example_item = ExampleItem()
        example_item["url"] = response.url
        example_item["description"] = response.xpath("//*/head/meta[@name='description']/@content").get()
        example_item["product"] = response.xpath("//*/nav[contains(@class, 'theme-doc-breadcrumbs')]/ul/li[2]//span/text() | //*/nav[contains(@class,'menu')]/ul/li[1]//a/text()").get()
        example_item["title"] = response.css("header h1::text").get()
        context = response.css(".theme-doc-markdown.markdown *::text").getall()
        cleaned_context = " ".join(context).replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')  # ZWSP, ZWNJ, ZWJ 삭제
        reString = re.sub('\$  node  app.js 20210309  07:45:59 .+ (\d{8})', '', re.sub('Nov  16 ,  2016   3 :06:40 AM [^>]+ (\d{8})', '', re.sub('start.sh \$ \./start.sh [^>]+ (\d{8}|\w{8})', '', cleaned_context)))
        example_item["contents"] = reString
        return example_item

    def parse_pass(self, response):
        pass
