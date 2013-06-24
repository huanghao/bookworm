import os
import sys
import argpase

import requests
import requests_cache
requests_cache.install_cache('cache')

from pyquery import PyQuery as pq

import douban
import amazon_cn
import ishare
from util import urlopen, get_url_hostpath


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
        'amazon.cn': amazon_cn.parse,
        'amazon.com': amazon_cn.parse,
        'douban.com/subject/': douban.parse,
        'ishare.iask.sina.com.cn': ishare.parse,
        }
    #TODO:
    #itpub.net, iter comments find download
    #verycd
    #ebook.jiani.info

    info = {}
    for href in hrefs:
        hostpath = get_url_hostpath(href)
        for site, parser in parsers.iteritems():
            if site not in info and hostpath.find(site) > -1:
                print 'parsing', href
                info[site] = parser(href)

    from pprint import pprint
    pprint(info)

    

def parse_args():
    parser = argparse.ArgumentParser(description='''search images.google by image file,
and get it's meta info from website such as amazon and douban.''')
    parser.add_argument('image', type=os.path.abspath,
        help='image to search')
    parser.add_argument('-o', '--output-file',
        help='save info into output file')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        search_by_image(filename)
    else:
        get_search_result(open('test.url').read().strip())
