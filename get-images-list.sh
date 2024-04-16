 rm images.json
 scrapy runspider --set FEED_EXPORT_ENCODING=utf-8 --set FEED_EXPORT_INDENT=2 get-all-images.py -o images.json