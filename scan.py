import os
import hashlib

from util import get_ext


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
                fingerprint = calculate_fingerprint(full_path, bs)
                ext = get_ext(name)
                yield FileData(fingerprint, ext, full_path)
