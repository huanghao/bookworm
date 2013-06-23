from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.http import Request


class DoubanWish(BaseSpider):

    name = 'douban/wish'
    allowed_domains = ['douban.com']
    start_urls = ['http://book.douban.com/people/huang1hao/wish']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        # wish item
        for href in hxs.select('//a[contains(@class, "nbg")]/@href').extract():
            yield Request(href, callback=self.parse_subject)
            break

        # next page
        for href in hxs.select('//span[contains(@class, "next")]/a').extract():
            yield Request(href, classback=self.parse)

    def parse_subject(self, response):
        hxs = HtmlXPathSelector(response)

        title = hxs.select('//h1/span/text()').extract()
        if title: title = title[0]
        print title

        mainpic = hxs.select('//div[@id="mainpic"]/a/@href').extract()
        if mainpic: mainpic = mainpic[0]
        print mainpic

        '''
        for info in hxs.select('//div[@id="info"]'):
            break
        print info
        '''

        tags = hxs.select('//div[@id="db-tags-section"]//a/text()').extract()
        print '\n'.join(tags)
