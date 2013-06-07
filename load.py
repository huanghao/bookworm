import os
import hashlib

import db


LIBS = ['~/Documents/ebook']

def fingerprint(path, block_size=4096):
    '''
    get fingerprint of a file, this info is consist of:
    * file size
    * md5 of the first block
    '''
    with open(path) as file_:
        sample = file_.read(block_size)
        stat = os.fstat(file_.fileno())

    return (stat.st_size, hashlib.md5(sample).hexdigest())

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
    for path in paths:
        path = os.path.expanduser(path)
        bs = os.statvfs(path).f_bsize

        for root, dirs, files in os.walk(path):
            for name in files:
                if filter_ and not filter_(name):
                    continue
                full_path = os.path.join(root, name)
                yield full_path, fingerprint(full_path, bs)


class FileData(object):

    def __init__(self, fingerprint, format, path):
        self.size = fingerprint[0]
        self.fingerprint = '.'.join((str(i) for i in fingerprint)).lower()
        self.format = format
        self.path = path


def diff(left, right):
    def process():
        pass

    lkey = left.next()
    if lkey is None:


    rkey = right.next()

    while 1:
        if lkey is None or rkey is None:
            break

        if lkey == rkey:
            lkey = left.next()
            rkey = right.next()
        elif lkey < rkey:
            lkey = left.next()
        else:
            rkey = right.next()

    if lkey is None:
        for
        pass


def main():
    for path, fingerprint in scan(LIBS, make_ext_filter('pdf')):
        fdata = FileData(fingerprint, get_ext(path), path)
        db.api.
        print fdata.format, fdata.size, fdata.fingerprint
    #for line in sys.stdin:
    #    md5, name = line.split(None, 1)

main()




