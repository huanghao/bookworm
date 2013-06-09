import sys
import logging
import argparse

from scan import scan, make_ext_filter
from repo import Repo, RepoItem
from queue import QueueItem


logger = logging.getLogger('updater')


def update(repo_path, lib_paths, max_read=None):
    repo = Repo(repo_path)
    queue = repo.new_queue()
    n = 0

    for info in scan(lib_paths, make_ext_filter('pdf')):
        key = info.fingerprint
        status = repo.check(key)
        if status == RepoItem.Status.OK:
            if repo.merge_path(key, info.path):
                logger.info('path updated: %s' % key)
        elif status == RepoItem.Status.DoesNotExist:
            if repo.put(key, info):
                logger.info('new file added: %s' % key)
                queue.add(QueueItem(key))

                n += 1
                if max_read and n >= max_read:
                    break

    queue.save()


def parse_args():
    parser = argparse.ArgumentParser(description='Scan files in lib paths to update meta info into repo, finally create a queue file into repo root.')
    parser.add_argument('repo_path')
    parser.add_argument('lib_paths', nargs='+')
    parser.add_argument('-n', '--max-read', type=int,
        help='number of files to read at most')
    parser.add_argument('-v', '--verbose',
        help='turn on verbose mode', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    opts = parse_args()
    level = logging.DEBUG if opts.verbose else logging.INFO
    logging.basicConfig(level=level, stream=sys.stdout)
    sys.exit(update(opts.repo_path, opts.lib_paths, opts.max_read))
