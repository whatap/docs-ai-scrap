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
    sitemap_rules = [
        ('/agent-transaction-error-stack', 'parse'),
        # ('/agent-transaction', 'parse_options'),
        # ('/agent-control-function', 'parse_options'),
        # ('/agent-usage', 'parse_options'),
        # ('/agent-network', 'parse_options'),
        # ('/agent-performance', 'parse_options'),
        # ('/agent-log', 'parse_options'),
        # ('/agent-transaction', 'parse_options'),
        # ('/agent-dbsql', 'parse_options'),
        # ('/agent-httpcapicall', 'parse_options'),
        # ('/agent-httpcapi', 'parse_options'),
        # ('/agent-httpcall', 'parse_options'),
        # ('/agent-number-of-user', 'parse_options'),
        # ('/agent-load-amount', 'parse_options'),
        # ('/agent-notification', 'parse_options'),
        # ('/agent-static', 'parse_options'),
        # ('/agent-toplogy', 'parse_options'),
        # ('/agent-additional-option', 'parse_options'),
        # ('/agent-shared-memory', 'parse_options'),
        # ('/agent-webservice', 'parse_options'),
        # ('/agent-library', 'parse_options'),
        # ('/kubernetes/set-agent', 'parse_options'),
        # ('/agent-dbx-settings', 'parse_options'),
        # ('/agent-xos-settings', 'parse_options'),
        # ('/agent-aws', 'parse_options'),
        # ('/agent-data', 'parse_options'),
        # ('/agent-xcub-settings', 'parse_options'),
        # ('/log/log-java', 'parse_options'),
        # ('opentelemetry/set-agent', 'parse_options'),
        ('/log/log-intro', 'parse_pass'),
        ('/log/log-flex', 'parse_pass'),
        ('/golang/topology-settings', 'parse_pass'),
        ('/golang/agent-troubleshooting', 'parse_pass'),
        ('/db/db-monitoring-intro', 'parse_pass'),
        ('/aws-log/metrics-intro', 'parse_pass'),
        ('/apm/java-supported-spec', 'parse_pass'),
        ('/apm/golang-supported-spec', 'parse_pass'),
        ('/apm/application-intro', 'parse_pass'),
        ('/whatap_guide/install_agent/server/support_env', 'parse_pass'),
        ('/use_guide/url_monitoring/intro', 'parse_pass'),
        ('/kr/user_guide_url', 'parse_pass'),
        ('/kr/appendix', 'parse_pass'),
        ('/dl-release-notes', 'parse_pass'),
        ('/navigation/int-dashboard', 'parse_pass'),
        ('/navigation/int-metrics-board', 'parse_pass'),
        ('/dashboard/acw-dashboard-ds', 'parse_pass'),
        ('/whatap_guide/install_agent/server/support_env', 'parse_pass'),
        ('/search/', 'parse_pass'),
        ('/license/', 'parse_pass'),
        ('/reference', 'parse_pass'),
        ('/release-notes/', 'parse_pass'),
        ('', 'parse')
    ]

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
                        # option_data = option_name, desc_string
                        option_data = {
                            # "name": option_name,
                            # "type": option_type,
                            # "default": default_val,
                            # "description": desc_string
                            option_name: desc_string
                        }
                        options_list.append(option_data)
                else:
                    pass
            # content_data = {
            #     "agent_options": options_list
            # }
            contents = [json.dumps(item, ensure_ascii=False) for item in options_list ]
            # contents.append(content_data)

        example_item["contents"] = ", ".join(contents)
        return example_item


    def parse(self, response):
        example_item = ExampleItem()
        example_item["url"] = response.url
        example_item["description"] = response.xpath("//*/head/meta[@name='description']/@content").get()
        example_item["product"] = response.xpath("//*/nav[contains(@class, 'theme-doc-breadcrumbs')]/ul/li[2]//span/text() | //*/nav[contains(@class,'menu')]/ul/li[1]//a/text()").get()
        example_item["title"] = response.css("header h1::text").get()
        context = response.css(".theme-doc-markdown.markdown *::text").getall()
        # example_item["contents"] = " ".join(context).replace('\u200b', '')
        cleaned_context = " ".join(context).replace('\u200b', '').replace('\u200c', '').replace('\u200d', '').replace('\n ', '')  # ZWSP, ZWNJ, ZWJ 삭제
        # start.sh \$ \./start.sh [^>]+ (\d{8}|\w{8})
        # Nov  16 ,  2016   3 :06:40 AM [^>]+ (\d{8})
        # \$  node  app.js 20210309  07:45:59 .+ (\d{8})
        reString = re.sub('\$  node  app.js 20210309  07:45:59 .+ (\d{8})', '', re.sub('Nov  16 ,  2016   3 :06:40 AM [^>]+ (\d{8})', '', re.sub('start.sh \$ \./start.sh [^>]+ (\d{8}|\w{8})', '', cleaned_context)))
        example_item["contents"] = reString
        return example_item

    def parse_pass(self, response):
        pass
