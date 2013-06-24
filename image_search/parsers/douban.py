#coding: utf8
import re

from pyquery import PyQuery as pq

from util import urlopen, parse_pair


class Douban(object):

    pattern = 'douban.com/subject/'

    def parse(self, url):
        info = {'url': url}
        html = pq(urlopen(url).content)

        # cover image url
        mainpic = html('#mainpic')
        cover_url = mainpic('a').attr('href')
        info['cover_url'] = cover_url
        print cover_url

        # title
        title = mainpic('img').attr('alt')
        info['title'] = title
        print title

        key_mapping = {
            u'作者': 'author',
            u'译者': 'translator',
            u'出版社': 'publisher',
            u'原作名': 'original title',
            u'出版年': 'published year',
            u'页数': 'num of pages',
            u'定价': 'price',
            u'装帧': 'paperback',
            u'丛书': 'series',
            }
        # author, publisher, pub year, price, isbn etc.
        desc = html('#info').html()
        for each in re.split(r'<br/?>', desc):
            each = each.strip()
            if each:
                k, v = parse_pair(pq(each).text())
                if k == u'页数':
                    try:
                        info['num of pages'] = int(v)
                    except ValueError:
                        info['num of pages'] = v
                else:
                    k = key_mapping.get(k, k).lower()
                    info[k] = v
                print u'{} => {}'.format(k, v)

        # tags
        tags = [ pq(a).text() for a in html('#db-tags-section')('a') ]
        info['tags'] = tags
        print ' '.join(tags)
        
        return info
