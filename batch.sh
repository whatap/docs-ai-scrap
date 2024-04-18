rm whatap-docs.json
scrapy runspider --set FEED_EXPORT_ENCODING=utf-8 --set FEED_EXPORT_INDENT=2 main.py -o whatap-docs.json