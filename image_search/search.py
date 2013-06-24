import os
import sys
import json
import logging
import argparse

import requests
import requests_cache

from pyquery import PyQuery as pq

from util import urlopen, get_url_hostpath, discover_parsers

logger = logging.getLogger(os.path.basename(__file__)[:-3])


def get_search_result(url):
    r = urlopen(url)
    html = pq(r.content)

    hrefs = []
    for link in html('.r')('a'):
        href = link.attrib['href']
        hrefs.append(href)
        logger.info('result %s: %s', link.text, href)

    info = {}
    for href in hrefs:
        hostpath = get_url_hostpath(href)
        for site, parser in parsers.iteritems():
            if site not in info and hostpath.find(site) > -1:
                logger.debug('parsing %s', href)
                info[site] = parser.parse(href)

    return info


def upload_image_and_get_search_link(image):
    url = 'http://images.google.com/searchbyimage/upload'

    data = {'image_content': ''}
    files = {'encoded_image': open(image, 'rb')}
    r = requests.post(url, data=data, files=files, allow_redirects=False)

    url = r.headers.get('location')
    logger.info('search link: %s', url)
    return url


def main(args):
    if args.debug:
        url = open(args.link_filename).read().strip()
    else:
        url = upload_image_and_get_search_link(args.image)
        if not args.not_save_search_link:
            with open(args.link_filename, 'w') as fp:
                fp.write(url)

    result = get_search_result(url)

    result_str = json.dumps(result, indent=4)
    logger.info('result: %s', result_str)

    if args.output_file:
        with open(args.output_file, 'w') as fp:
            fp.write(result_str)
        logger.info('result is saved in %s', args.output_file)


def parse_args():
    parser = argparse.ArgumentParser(description='''search images.google by
image file,and get it's meta info from website such as amazon and douban.''')
    parser.add_argument('image', type=os.path.abspath,
                        help='image to search')
    parser.add_argument('-o', '--output-file',
                        help='save info into output file')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='turn on debug mode')
    parser.add_argument('-S', '--not-save-search-link', action='store_true',
                        help='''save search link returned by google into
a text file, it can be used in debug mode''')
    parser.add_argument('--link-filename', default='test.url',
                        help='the file name which -s used to save url')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    if args.debug:
        requests_cache.install_cache('cache')

    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level, stream=sys.stdout)

    parsers = discover_parsers()
    if not parsers:
        logger.error('Can\'t find any parser')
        sys.exit(1)

    sys.exit(main(args))
        
