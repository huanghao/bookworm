from pyquery import PyQuery as pq

from bookworm.image_search.util import urlopen, parse_pair


class AmazonCom(object):

    pattern = 'amazon.com'

    def parse(self, url):
        info = {'url': url}
        html = pq(urlopen(url).content)

        # cover image url
        cover = html('#main-image')
        cover_url = cover.attr('src')
        info['cover_url'] = cover_url
        print cover_url

        # title and author
        title = html('.parseasinTitle')
        info['title'] = title.text()
        print info['title']

        author = title.siblings('span').text()
        info['author'] = author
        print author

        # price
        for label in html('.rentalPriceLabel'):
            label = pq(label)
            if label.text().strip().lower() == 'buy new':
                price = label.siblings('.rentPrice').text()
                info['price'] = price
                print price
                break

        # basic info, such as publisher, lanuage, num of pages, IBSN, etc.
        for li in html('#SalesRank').parents('ul').children('li'):
            li = pq(li)
            k, v = parse_pair(pq(li).text())
            k = k.lower()
            if k in ('shipping weight',
                     'average customer review',
                     'amazon best sellers rank'):
                continue
            if k in ('paperback', 'hardcover'):
                info['binding'] = k
                try:
                    info['num of pages'] = int(v.replace('pages', ''))
                except ValueError:
                    info['num of pages'] = v
            else:
                info[k] = v
            print u'{} => {}'.format(k, v)

        return info

