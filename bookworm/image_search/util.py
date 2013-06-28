import random
import inspect
import urlparse
from pkgutil import iter_modules

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

def walk_modules(path, load=False):
    """Loads a module and all its submodules from a the given module path and
    returns them. If *any* module throws an exception while importing, that
    exception is thrown back.

    For example: walk_modules('scrapy.utils')
    """

    mods = []
    mod = __import__(path, {}, {}, [''])
    mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(mod.__path__):
            fullpath = path + '.' + subpath
            if ispkg:
                mods += walk_modules(fullpath)
            else:
                submod = __import__(fullpath, {}, {}, [''])
                mods.append(submod)
    return mods


def discover_parsers():
    def iter_parsers():
        for module in walk_modules('bookworm.image_search.parsers'):
            for obj in vars(module).itervalues():
                if inspect.isclass(obj) and \
                        callable(getattr(obj, 'parse', None)) and \
                        hasattr(obj, 'pattern'):
                    yield obj

    parsers = {}
    for parser_cls in iter_parsers():
        if isinstance(parser_cls.pattern, list):
            for p in parser_cls.pattern:
                parsers[p] = parser_cls()
        else:
            parsers[parser_cls.pattern] = parser_cls()
    #TODO:
    #itpub.net, iter comments find download
    #verycd
    #ebook.jiani.info
    return parsers
