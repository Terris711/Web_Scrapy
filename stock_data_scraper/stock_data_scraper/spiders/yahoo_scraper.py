import scrapy


class YahooScraperSpider(scrapy.Spider):
    name = "yahoo_scraper"
    allowed_domains = ["finance.yahoo.com"]
    start_urls = ["http://finance.yahoo.com/"]

    def start_requests(self):
        urls = ['https://finance.yahoo.com/quote/ETRN/']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        pass
