import random
import urlparse

import requests


USER_AGENTS = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',
    'Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'
    )

def urlopen(url):
    return requests.get(url, headers={'User-Agent': random.choice(USER_AGENTS)})

def parse_pair(s):
    # replace chinese colon to english
    return [ i.strip() for i in s.replace(u'\uff1a', ':').split(':', 1) ]

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

