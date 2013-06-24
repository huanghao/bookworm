from pyquery import PyQuery as pq

from util import urlopen, parse_pair


class AmazonCN(object):

    pattern = [
        'amazon.cn',
        'amazon.com',
        ]

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
        #print title.text()
        title_and_author = title.parents('.buying').text()
        info['title_and_author'] = title_and_author
        print title_and_author

        # price
        list_price = html('#listPriceValue').text()
        actual_price = html('#actualPriceValue').text()
        info['price'] = list_price
        print list_price
        print actual_price

        # basic info, such as publisher, lanuage, num of pages, IBSN, etc.
        for li in html('#SalesRank').parents('ul').children('li'):
            li = pq(li)
            if li.is_('#SalesRank'):
                continue
            k, v = parse_pair(pq(li).text())
            info[k] = v
            print u'{} => {}'.format(k, v)

        return info

