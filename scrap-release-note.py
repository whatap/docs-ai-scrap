import scrapy
import re
from datetime import datetime

class ReleaseSpider(scrapy.Spider):
    name = 'whatap-release'
    start_urls = [ 
        'https://docs.whatap.io/en/release-notes/java/java-2_2_36',
        'https://docs.whatap.io/en/release-notes/java/java-2_2_35',
        'https://docs.whatap.io/en/release-notes/java/java-2_2_34',
        'https://docs.whatap.io/en/release-notes/java/java-2_2_33',
        'https://docs.whatap.io/en/release-notes/java/java-2_2_32',
        'https://docs.whatap.io/en/release-notes/java/java-2_2_31',
        'https://docs.whatap.io/en/release-notes/java/java-2_2_30',
        'https://docs.whatap.io/en/release-notes/java/java-2_2_29',
        'https://docs.whatap.io/en/release-notes/java/java-2_2_28',
        'https://docs.whatap.io/en/release-notes/java/java-2_2_27',
        'https://docs.whatap.io/en/release-notes/java/java-2_2_26'
    ]

    def convert_date(self, date_str):
        # 각 형식에 대한 패턴 정의
        patterns = [
            ('%B %d, %Y', '%Y-%m-%d'),  # 'May 28, 2024'
            ('%Y년 %m월 %d일', '%Y-%m-%d'),  # '2024년 05월 28일'
            ('%Y年%m月%d日', '%Y-%m-%d')  # '2024年05月28日'
        ]
        
        # 패턴에 따라 변환 시도
        for input_pattern, output_pattern in patterns:
            try:
                # 문자열을 datetime 객체로 변환
                date_obj = datetime.strptime(date_str, input_pattern)
                # datetime 객체를 원하는 형식의 문자열로 변환
                return date_obj.strftime(output_pattern)
            except ValueError:
                # 패턴이 맞지 않으면 다음 패턴으로 이동
                continue
        # 모든 패턴이 맞지 않으면 에러 메시지 반환
        return "Date format not recognized"

    def start_requests(self):
        for url in self.start_urls:
            if 'service' in url:
                yield scrapy.Request(url, callback=self.parse)
            else:
                yield scrapy.Request(url, callback=self.parseagent)

    def remove_zero_width_space(self, text):
        # Zero Width Space (U+200B)를 제거
        return text.replace('\u200B', '')

    def extract_change_items(self, node, ver, prodName, category):
        items = []
        next_sibling_ul = node.xpath('(following-sibling::*[1][self::ul] | following-sibling::*[1][self::p[not(img)]])')
        if node.xpath('( .//code[@class="Fixed"] | .//code[@class="Changed"] | .//code[@class="Feature"] | .//code[@class="Deprecated"] | .//code[@class="Deprecate"] | .//code[@class="New"] )'):
            changetype = self.remove_zero_width_space(node.xpath('.//code/text()').get())
            # desc = [self.remove_zero_width_space(d) for d in node.getall()]
            desc = self.remove_zero_width_space(node.get())
            hashid = ver.lower().replace('.', '').replace(' ', '-')
            item = {
                "ver": ver,
                "hash": hashid,
                "product": prodName,
                "type": changetype,
                "desc": desc
            }
            if category:
                item["category"] = category
            
            if next_sibling_ul:
              details_content = self.remove_zero_width_space(next_sibling_ul.get())
              details = re.sub('<p><img decoding=\\"async\\" loading=\\"lazy\\" src=\\"([^>]+?)\\" width=\\"(\d+)\\" height=\\"(\d+)\\" class=\\"([^>]+)?\\"></p>\\n', '', details_content)
              item["details"] = details
            items.append(item)
        return items

    def parse(self, response):
        sections = response.xpath("//section")

        for section in sections:
            ver = section.xpath('.//h2/text()').get()
            dateStr = section.xpath('.//h2/following-sibling::p[1]/text()').get()
            date = self.convert_date(dateStr)
            nodes = section.xpath('.//div[@class="indentTab"]/*')
            prodName = None
            category = None
            items = []

            for node in nodes:
                tag = node.root.tag
                if tag == 'h3':
                    prodName = self.remove_zero_width_space(node.xpath('string()').get())
                    category = None
                elif tag == 'h4':
                    category = self.remove_zero_width_space(node.xpath('string()').get())
                elif tag == 'ul':
                    lists = node.xpath('.//li')
                    if len(lists) == 1 and not lists.xpath('.//p'):
                        # li가 하나만 있고, li 안에 p가 없는 경우
                        items.extend(self.extract_change_items(lists[0], ver, prodName, category))
                    elif len(lists) > 1:
                        # 일반적인 경우
                        for list_item in lists.xpath('.//p'):
                            items.extend(self.extract_change_items(list_item, ver, prodName, category))
                elif tag == 'p':
                    items.extend(self.extract_change_items(node, ver, prodName, category))

            result = {
                "url": response.url,
                "ver": ver,
                "date": date,
                "Lists": items
            }
            yield result

    def parseagent(self, response):
        header = self.remove_zero_width_space(response.xpath('//header/h1/text()').get())
        dateStr = self.remove_zero_width_space(response.xpath('.//header/following-sibling::p[1]/text()').get())
        date = self.convert_date(dateStr)
        ver = re.search('v[\d\.]+', header).group()
        prodName = header.replace(ver, '').strip()

        # check section
        sections = response.xpath('//div[@class="theme-doc-markdown markdown"]/section')
        if len(sections) > 0:
            nodes = response.xpath('//div[@class="theme-doc-markdown markdown"]/section/*')
        elif len(sections) == 0:
            nodes = response.xpath('//div[@class="theme-doc-markdown markdown"]/*')

        items = []

        category = None
        for idx, node in enumerate(nodes):
            tag = node.root.tag
            if tag == 'header':
                continue
            if tag == 'p':
                # check 날짜
                if node.xpath('string()').get() == dateStr:
                    continue
                else:
                    items.extend(self.extract_change_items(node, ver, prodName, category))
            if tag == 'h2' or tag == 'h3':
                category = self.remove_zero_width_space(node.xpath('string()').get())
            if tag == 'ul':
                lists = node.xpath('.//li')
                if len(lists) == 1 and not lists.xpath('.//p'):
                    # li가 하나만 있고, li 안에 p가 없는 경우
                    items.extend(self.extract_change_items(lists[0], ver, prodName, category))
                elif len(lists) > 1:
                    # 일반적인 경우
                    for list_item in lists.xpath('.//p'):
                        items.extend(self.extract_change_items(list_item, ver, prodName, category))
            if tag == 'hr':
                pass

        result = {
            "url": response.url,
            "ver": ver,
            "date": date,
            "Lists": items
        }
        yield result