import scrapy

class ReleaseSpider(scrapy.Spider):
    name = 'whatap-release'
    start_urls = [ 
        'https://docs.whatap.io/release-notes/service/service-2_0_x'
    ]

    def remove_zero_width_space(self, text):
        # Zero Width Space (U+200B)를 제거
        return text.replace('\u200B', '')

    def extract_change_items(self, node, ver, prodName, category):
        items = []
        next_sibling_ul = node.xpath('(following-sibling::*[1][self::ul] | following-sibling::*[1][self::p[not(img)]])')
        if node.xpath('( .//code[@class="Fixed"] | .//code[@class="Changed"] | .//code[@class="Feature"] | .//code[@class="Deprecated"] | .//code[@class="New"] )'):
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
              details = self.remove_zero_width_space(next_sibling_ul.get())
            #   details = [self.remove_zero_width_space(d) for d in next_sibling_ul.getall()]
              item["details"] = details
            items.append(item)
        return items

    def parse(self, response):
        sections = response.xpath("//section")

        for section in sections:
            ver = section.xpath('.//h2/text()').get()
            dateStr = section.xpath('.//h2/following-sibling::p[1]/text()').get()
            date = dateStr.replace('년 ', '-').replace('월 ', '-').replace('일', '')
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
