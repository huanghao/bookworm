import re

from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.http import Request

from grabber.items import Book


TAG = re.compile(r'<.*?>', re.M)
def tag_strip(s):
    return TAG.sub('', s)

def parse_dict(s):
    s = s.strip().replace(u'\uff1a', ':')
    lines = filter(None, [ i.strip() for i in s.split('\n') ])
    
    processed = []
    for line in lines:
        if line.find(':') < 0 and processed:
            # if there aren't both key and value, append to last line
            processed[-1] += ' ' + line
        else:
            processed.append(line)

    return dict([ [ i.strip() for i in line.split(':', 1) ] 
                  for line in processed ])


class DoubanWish(BaseSpider):

    name = 'douban'
    allowed_domains = ['douban.com']
    start_urls = [
        'http://book.douban.com/people/huang1hao/wish',
        'http://book.douban.com/people/huang1hao/collect',
        'http://book.douban.com/people/huang1hao/do',
        ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        # wish item
        for href in hxs.select('//a[contains(@class, "nbg")]/@href').extract():
            yield Request(href, callback=self.parse_subject)

        # next page
        for href in hxs.select('//span[contains(@class, "next")]/a/@href').extract():
           yield Request(href, callback=self.parse)

    def parse_subject(self, response):
        hxs = HtmlXPathSelector(response)

        title = hxs.select('//h1/span/text()').extract()
        if title: title = title[0]
        print 'title:', title

        mainpic = hxs.select('//div[@id="mainpic"]/a/@href').extract()
        if mainpic: mainpic = mainpic[0]
        print 'mainpic:', mainpic

        info = hxs.select('//div[@id="info"]').extract()
        if info:
            info = tag_strip(info[0])
            info = parse_dict(info)
            for k, v in info.iteritems():
                print u'{}: {}'.format(k, v)

        tags = hxs.select('//div[@id="db-tags-section"]//a/text()').extract()
        print 'tags:', '|'.join(tags)

        yield Book(title=title,
                   cover_link=mainpic,
                   info=info,
                   tags=tags,
                   )
