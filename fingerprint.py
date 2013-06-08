#!/usr/bin/env python
import os
import sys
import hashlib


class Fingerprint(object):
    '''Fingerprint of a file, which contains information calcuate by
    its file size and md5sum of the first data block
    '''

    def __init__(self, path, block_size=None):
        self.path = path
        self.block_size = block_size or os.statvfs(path).f_bsize
        self.size, self.md5 = None, None

    def calculate(self):
        with open(self.path) as file_:
            sample = file_.read(self.block_size)
            stat = os.fstat(file_.fileno())

        self.size = stat.st_size
        self.md5 = hashlib.md5(sample).hexdigest().lower()
        return self.size, self.md5

    def hex(self):
        if self.size is None:
            self.calculate()
        return '%s%x' % (self.md5, self.size)

    def __str__(self):
        return self.hex()


if __name__ == '__main__':
    for path in sys.argv[1:]:
        print '%s\t%s' % (str(Fingerprint(path)), path)
