#coding: utf8
from pyquery import PyQuery as pq

from image_search.util import urlopen, parse_pair


class AmazonCn(object):

    pattern = 'amazon.cn'

    def parse(self, url):
        info = {'url': url}
        html = pq(urlopen(url).content)

        # cover image url
        cover = html('#original-main-image')
        cover_url = cover.attr('src')
        info['cover_url'] = cover_url
        print cover_url

        # title and author
        title = html('.parseasinTitle')
        info['title'] = title.text()
        print info['title']

        title_and_author = title.parents('.buying').text()
        author = title_and_author.replace(info['title'], '').strip()
        info['author'] = author
        print author

        # price
        list_price = html('#listPriceValue').text()
        actual_price = html('#actualPriceValue').text()
        info['price'] = list_price or actual_price
        print info['price']

        key_mapping = {
            u'出版社': 'publisher',
            u'语种': 'language',
            u'条形码': 'isbn-13',
            u'商品尺寸': 'product dimensions',
            u'商品重量': 'shipping weight',
            u'外文书名': 'original title',
            }
        # basic info, such as publisher, lanuage, num of pages, IBSN, etc.
        for li in html('#SalesRank').parents('ul').children('li'):
            li = pq(li)
            k, v = parse_pair(pq(li).text())
            if k in (u'用户评分', u'亚马逊热销商品排名'):
                continue
            if k == u'平装':
                info['binding'] = 'paperback'
                try:
                    info['num of pages'] = int(v.replace('页', ''))
                except ValueError:
                    info['num of pages'] = v
            elif k == u'精装':
                info['binding'] = 'hardcover'
                try:
                    info['num of pages'] = int(v.replace('页', ''))
                except ValueError:
                    info['num of pages'] = v
            else:
                k = key_mapping.get(k, k).lower()
                info[k] = v
            print u'{} => {}'.format(k, v)

        return info

