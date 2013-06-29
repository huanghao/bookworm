import os
import sys
import logging
import argparse

from bookworm.repo import Repo, key_to_path
from bookworm.indexdb import DB

logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])


def main(args):
    if not os.path.isdir(args.db_path):
        logger.error('db path does not exist(%s), '
        'please use -d to specify a correct db path' % args.db_path)
        return 1
    if not os.path.isdir(args.repo_path):
        logger.error('repo path does not exist(%s), '
        'please use -r to specify a correct repo path' % args.repo_path)
        return 1

    db = DB(args.db_path)
    if args.keys:
        for key in args.keys:
            itempath = os.path.join(args.repo_path, key_to_path(key))
            db.index(key, itempath, args.force_index)
    else:
        for key, itempath in Repo(args.repo_path).walk():
            db.index(key, itempath, args.force_index)


def parse_args():
    parser = argparse.ArgumentParser(description='''Search repo to index all book
    If there are queue files in root path of repo, it will only deal with those
    queue files. Otherwise it could walk through the whole repo to index them
    all.''')
    parser.add_argument('keys', nargs='*', help='key to index')
    parser.add_argument('-d', '--db-path', default='db',
        help='xapian db root path')
    parser.add_argument('-r', '--repo-path', default='repo',
        help='ebook repo root path')
    parser.add_argument('-f', '--force-index', action='store_true',
                        help='force index even if it exists')
    parser.add_argument('-v', '--verbose',
        action='store_true', help='turn on verbose mode')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, stream=sys.stdout)

    sys.exit(main(args))
