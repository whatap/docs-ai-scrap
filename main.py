import json
import scrapy
import re
from scrapy.spiders import SitemapSpider

class DocsItem(scrapy.Item):
    url = scrapy.Field()
    description = scrapy.Field()
    product = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    header = scrapy.Field()

class Coolspider(SitemapSpider):
    name = "whatapDocs"
    sitemap_urls = ["https://docs.whatap.io/sitemap.xml"]
    sitemap_rules = [
        ('https://docs.whatap.io/java/', 'parse'),
        ('https://docs.whatap.io/php/', 'parse'),
        ('https://docs.whatap.io/python/', 'parse'),
        ('https://docs.whatap.io/nodejs/', 'parse'),
        ('https://docs.whatap.io/dotnet/', 'parse'),
        ('https://docs.whatap.io/golang/', 'parse'),
        ('https://docs.whatap.io/server/', 'parse'),
        ('https://docs.whatap.io/kubernetes/', 'parse'),
        ('https://docs.whatap.io/postgresql/', 'parse'),
        ('https://docs.whatap.io/oracle/', 'parse'),
        ('https://docs.whatap.io/mysql/', 'parse'),
        ('https://docs.whatap.io/mssql/', 'parse'),
        ('https://docs.whatap.io/tibero/', 'parse'),
        ('https://docs.whatap.io/cubrid/', 'parse'),
        ('https://docs.whatap.io/altibase/', 'parse'),
        ('https://docs.whatap.io/redis/', 'parse'),
        ('https://docs.whatap.io/mongodb/', 'parse'),
        ('https://docs.whatap.io/url/', 'parse'),
        ('https://docs.whatap.io/amazon-cloudwatch/', 'parse'),
        ('https://docs.whatap.io/amazon-ecs/', 'parse'),
        ('https://docs.whatap.io/azure/', 'parse'),
        ('https://docs.whatap.io/ncloud/', 'parse'),
        ('https://docs.whatap.io/oracle-cloud/', 'parse'),
        ('https://docs.whatap.io/browser', 'parse'),
        ('https://docs.whatap.io/npm/', 'parse'),
        ('https://docs.whatap.io/log/', 'parse'),
        ('https://docs.whatap.io/aws-log/', 'parse'),
        ('https://docs.whatap.io/opentelemetry/', 'parse'),
        ('https://docs.whatap.io/focus/', 'parse'),
        ('https://docs.whatap.io/telegraf/', 'parse'),
        ('https://docs.whatap.io/about-billing', 'parse'),
        ('https://docs.whatap.io/software-proxy', 'parse'),
        ('https://docs.whatap.io/main-ui-intro-v2', 'parse'),
        ('https://docs.whatap.io/best-practice-guides', 'parse'),
        ('https://docs.whatap.io/whatap-overview', 'parse'),
        ('https://docs.whatap.io/welcome-to-whatapdocs', 'parse'),
        ('https://docs.whatap.io/support-env', 'parse'),
        ('https://docs.whatap.io/quick-guide', 'parse'),
        ('https://docs.whatap.io/mobile-app', 'parse'),
        ('https://docs.whatap.io/account', 'parse'),
        ('https://docs.whatap.io/project', 'parse'),
        ('https://docs.whatap.io/report', 'parse'),
        ('https://docs.whatap.io/notification', 'parse'),
        ('https://docs.whatap.io/management', 'parse'),
        ('https://docs.whatap.io/mxql', 'parse'),
        ('https://docs.whatap.io/faq', 'parse'),
        ('https://docs.whatap.io/glossary', 'parse'),
        ('https://docs.whatap.io/reference/', 'parse'),
    ]

    def parse(self, response):
        docs_item = DocsItem()
        title = response.css("header h1::text").get()
        meta_desc = response.xpath("//*/head/meta[@name='description']/@content").get()
        product = response.xpath(
            "//*/nav[contains(@class, 'theme-doc-breadcrumbs')]/ul/li[2]//span/text() | //*/nav[contains(@class,'menu')]/ul/li[1]//a/text()").get()

        # 섹션 개수 확인
        sections = response.xpath('//section')
        num_sections = len(sections)

        if num_sections ==  0:
            context = response.xpath('//*/div[@class="theme-doc-markdown markdown"]').xpath('string()').get()
            # JSON 형식으로 출력
            result = {
                "title": title,
                "url": response.url,
                "content": title + '. ' + meta_desc + ' ' + re.sub('(\\n)+', ' ', context),
                "product": product,
                "header": title  # 첫 번째 섹션 이전의 콘텐츠는 타이틀과 동일하다고 가정합니다.
            }
            yield result

        if num_sections > 0:
            # 첫 번째 섹션 이전의 모든 콘텐츠 요소 추출
            content_elements = response.xpath('(//p | //ul | //ol | //div | //table)/section[1]/preceding-sibling::*[not(self::header)]')
            # 첫 번째 섹션 이전의 모든 콘텐츠 추출
            pre_sections_content = ''
            for element in content_elements:
                pre_sections_content += element.xpath('string()').get() + " "

            # JSON 형식으로 출력
            result = {
                "title": title,
                "url": response.url,
                "content": title + '. ' + meta_desc + ' ' + re.sub('(\\n)+', ' ', re.sub(r'\u200b', '', pre_sections_content.strip())),
                "product": product,
                "header": title  # 첫 번째 섹션 이전의 콘텐츠는 타이틀과 동일하다고 가정합니다.
            }
            yield result

            for section in sections:
                if section.xpath('@class').get() == 'row':
                    continue
                # 하위 section 요소를 제외한 모든 자식 요소를 추출합니다.
                section_content = ""
                for element in section.xpath('./*[not(self::section or self::h2 or self::h3 or self::h4)]/descendant-or-self::text()'):
                    text = element.get().strip()
                    if text:
                        section_content += text + " "
                # for element in section.xpath('./*[not(self::section)]/descendant-or-self::text()'):
                #     text = element.get().strip()
                #     if text:
                #         section_content += text + " "

                # 섹션의 제목 추출
                header = section.xpath('.//h2/text() | .//h2/span/text() | .//h2/em/strong/text() | .//h2/strong/em/text() | .//h3/text() | .//h3/span/text() | .//h3/em/strong/text() | .//h3/strong/em/text() | .//h3/code/text() | .//h4/text() | .//h4/span/text() | .//h4/em/strong/text() | .//h4/strong/em/text()').get()

                if not section_content:
                    continue

                # JSON 형식으로 출력
                result = {
                    "url": response.url,
                    "title": title,
                    "content": header + '. ' + re.sub('(\\n)+', ' ', re.sub(r'\u200b', '', section_content.strip())),
                    "product": product,
                    "header": header
                }
                yield result

    def parse_pass(self, response):
        pass