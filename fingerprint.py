#!/usr/bin/env python
import os
import sys
import hashlib


def calculate_fingerprint(path, block_size=None):
    '''
    get fingerprint of a file, this info is consist of:
    * file size
    * md5 of the first block
    '''
    block_size = block_size or os.statvfs(path).f_bsize

    with open(path) as file_:
        sample = file_.read(block_size)
        stat = os.fstat(file_.fileno())

    return (stat.st_size, hashlib.md5(sample).hexdigest().lower())

def hex_fingerprint(path, block_size=None):
    size, fingerprint = calculate_fingerprint(path, block_size)
    return '%s%x' % (fingerprint, size)


if __name__ == '__main__':
    for path in sys.argv[1:]:
        hexfp = hex_fingerprint(path)
        print '%s %s' % (hexfp, path)
