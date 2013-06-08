import os

from fingerprint import Fingerprint


class Info(object):

    def __init__(self, fingerprint, size, format, path):
        self.fingerprint = fingerprint
        self.size = size
        self.format = format
        self.path = path.decode('utf8')

    def __str__(self):
        return '\t'.join([self.format,
                          self.fingerprint,
                          str(self.size),
                          self.path])


def get_ext(path):
    return os.path.splitext(path)[1].lstrip(os.path.extsep)


def make_ext_filter(wanted):
    '''
    make a filter function which will return true if given path
    in wanted or equals wanted
    '''
    def _filter(path):
        ext = get_ext(path)
        if type(wanted) in (list, tuple):
            return ext in wanted
        return ext == wanted
    return _filter


def scan(paths, filter_=None):
    '''
    walk through all paths given, for each file
    not filter out yield a Info object
    '''
    for path in paths:
        path = os.path.expanduser(path)
        bs = os.statvfs(path).f_bsize

        for root, dirs, files in os.walk(path):
            for name in files:
                if filter_ and not filter_(name):
                    continue
                ext = get_ext(name)
                full_path = os.path.join(root, name)
                fp = Fingerprint(full_path, bs)
                size, _ = fp.calculate()
                yield Info(fp.hex(), size, ext, full_path)


if __name__ == '__main__':
    import sys
    for info in scan(sys.argv[1:], make_ext_filter('pdf')):
        print str(info)
