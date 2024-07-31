rm test.json
scrapy runspider --set FEED_EXPORT_ENCODING=utf-8 --set FEED_EXPORT_INDENT=2 scrap-release-note.py -o test.json