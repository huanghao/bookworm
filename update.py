import sys
import logging

from scan import scan, make_ext_filter
from repo import Repo, RepoItem
from queue import QueueItem


logger = logging.getLogger('updater')


def update(repo_path, lib_paths):
    repo = Repo(repo_path)
    queue = repo.new_queue()

    #for info in head(scan(lib_paths, make_ext_filter('pdf')), n=2):
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

    queue.save()


def usage():
    print '''Usage: %s <repo_path> <lib_path1> [lib_path2 ...]

Scan files in lib paths to update meta info into repo,
finally create a queue file into repo root.''' % sys.argv[0]


if __name__ == '__main__':
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    repo_path = sys.argv[1]
    lib_paths = sys.argv[2:]

    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout)

    sys.exit(update(repo_path, lib_paths))
