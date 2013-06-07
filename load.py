import os
import hashlib

import db


LIBS = ['~/Documents/ebook']

def head(stream, n=10):
    i = 0
    for each in stream:
        if i < n:
            i += 1
            yield each
        else:
            break

def get_fingerprint(path, block_size=4096):
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


class FileData(object):

    def __init__(self, fingerprint, format, path):
        self.size = fingerprint[0]
        self.fingerprint = '.'.join((str(i) for i in fingerprint)).lower()
        self.format = format
        self.path = path

    def __str__(self):
        return '\t'.join([self.fingerprint, self.path])

    def __eq__(self, path_obj):
        '''
        path_obj is a instance of class db.Path
        '''
        return self.path == path_obj.path

    def __lt__(self, path_obj):
        return self.path < path_obj.path


def scan(paths, filter_=None):
    for path in paths:
        path = os.path.expanduser(path)
        bs = os.statvfs(path).f_bsize

        for root, dirs, files in os.walk(path):
            for name in files:
                if filter_ and not filter_(name):
                    continue
                full_path = os.path.join(root, name)
                fingerprint = get_fingerprint(full_path, bs)
                ext = get_ext(name)
                yield FileData(fingerprint, ext, full_path)




def diff(left, right):
    '''
    assume they are already sorted
    '''
    left_len = len(left)
    right_len = len(right)

    left_only = []
    right_only = []

    l, r = 0, 0
    while l < left_len and r < right_len:
        if left[l] == right[r]:
            l += 1
            r += 1
        elif left[l] < right[r]:
            left_only.append(left[l])
            l += 1
        else:
            right_only.append(right[r])
            r += 1

    if l >= left_len:
        while r < right_len:
            right_only.append(right[r])
            r += 1
    else:
        while l < left_len:
            left_only.append(left[l])
            l += 1

    return left_only, right_only


def main():
    fslist = head(scan(LIBS, make_ext_filter('pdf')), n=15)
    fslist = sorted(fslist, key=lambda fdata: fdata.path)

    dblist = db.api.get_paths().all()
    dblist = sorted(dblist, key=lambda path_obj: path_obj.path)
    #TODO: make faster, is there some distributed way to do this

    new, delete = diff(fslist, dblist)
    print len(new)
    print len(delete)

    db.api.add_filedata(new)


if __name__ == '__main__':
    main()
