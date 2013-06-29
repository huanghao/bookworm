#!/usr/bin/env python
import sys

from bookworm.util import Fingerprint


if __name__ == '__main__':
    if sys.stdin.isatty():
        files = sys.argv[1:]
    else:
        files = sys.stdin

    for path in files:
        path = path.rstrip()
        try:
            print '%s\t%s' % (str(Fingerprint(path)), path)
        except IOError as err: #[Errno 32] Broken pipe
            if err.errno == 32:
                break
            raise
