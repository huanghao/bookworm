import re
import sys
import random
import urlparse

import requests
import requests_cache
requests_cache.install_cache('cache')

from pyquery import PyQuery as pq


USER_AGENTS = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',
    'Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'
    )

def urlopen(url):
    return requests.get(url, headers={'User-Agent': random.choice(USER_AGENTS)})


def search_by_image(filename):
    url = 'http://images.google.com/searchbyimage/upload'

    data = {'image_content': ''}
    files = {'encoded_image': open(filename, 'rb')}

    r = requests.post(url, data=data, files=files, allow_redirects=False)

    url = r.headers.get('location')
    print 'location:', url
    with open('test.url', 'w') as fp:
        fp.write(url)

    get_search_result(url)

def get_url_host(url):
    parts = urlparse.urlsplit(url)
    host = '%s://%s' % (parts.scheme, parts.netloc)
    return host

def get_url_hostpath(url):
    parts = urlparse.urlsplit(url)
    hostpath = join_url_hostpath(parts.netloc, parts.path)
    return hostpath

def join_url_hostpath(host, path):
    return '/'.join([host, path.lstrip('/')])

def get_search_result(url):
    r = urlopen(url)
    html = pq(r.content)

    print '-'*40
    hrefs = []
    for link in html('.r')('a'):
        href = link.attrib['href']
        hrefs.append(href)
        print '* %s: %s' % (link.text, href)

    print '-'*40
    parsers = {
        'amazon.cn': parse_amazon_cn,
        'amazon.com': parse_amazon_cn,
        'douban.com/subject/': parse_douban,
        'ishare.iask.sina.com.cn': parse_ishare,
        }
    #TODO:
    #itpub.net, iter comments find download
    #verycd

    info = {}
    for href in hrefs:
        hostpath = get_url_hostpath(href)
        for site, parser in parsers.iteritems():
            if site not in info and hostpath.find(site) > -1:
                print 'parsing', href
                info[site] = parser(href)

    from pprint import pprint
    pprint(info)


def parse_pair(s):
    # replace chinese colon to english
    return [ i.strip() for i in s.replace(u'\uff1a', ':').split(':', 1) ]

def parse_ishare(url):
    info = {'url': url}
    html = pq(urlopen(url).content)

    # tilte
    title = html('h1.f14').text()
    info['title'] = title

    # download url
    btn = html('.download_btn_box')
    host = get_url_host(url)
    download_url = join_url_hostpath(host, btn('a').attr('href'))
    info['download_url'] = download_url
    print download_url

    # file size
    file_size = btn('span').text()
    info['file_size'] = file_size
    print file_size

    return info


def parse_douban(url):
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

    # author, publisher, pub year, price, isbn etc.
    desc = html('#info').html()
    for each in re.split(r'<br/?>', desc):
        each = each.strip()
        if each:
            k, v = parse_pair(pq(each).text())
            info[k] = v
            print u'{} => {}'.format(k, v)

    # tags
    tags = [ pq(a).text() for a in html('#db-tags-section')('a') ]
    info['tags'] = tags
    print ' '.join(tags)
    
    return info


def parse_amazon_cn(url):
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

    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        search_by_image(filename)
    else:
        get_search_result(open('test.url').read().strip())
