import os
import re
import sys


def find(top, filter_=None):
    for dirpath, dirnames, filenames in os.walk(top):
        for name in filenames:
            if filter_ is None or filter_(name):
                yield dirpath, name


def main():
    top = sys.argv[1]

    pattern = re.compile(r'.*\n.*\.pdf')
    name_filter = lambda name: pattern.match(name, re.M)

    for dirpath, filename in find(top, name_filter):
        path = os.path.join(dirpath, filename)
        print repr(path), '-->'

        newpath = path.replace('\n', '')
        os.rename(path, newpath)
        print repr(newpath)
        print

main()
