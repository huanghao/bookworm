import os
import sys
import time
import json
import logging
import datetime

from util import head, mkdir_p
from scan import scan, make_ext_filter
from reader import get_pdf_num_pages, get_pdf_text


logger = logging.getLogger('update')

def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class Item(object):

    def __init__(self, path):
        self.path = path
        self.meta_path = os.path.join(self.path, 'meta')
        self.text_path = os.path.join(self.path, 'text')

    def exists(self):
        return os.path.exists(self.text_path)

    def _write_info_to_meta(self, info):
        meta = {
            'key': info.fingerprint,
            'format': info.format,
            'size': info.size,
            'paths': {
                info.path: now(),
                },
            'num_pages': get_pdf_num_pages(info.path),
            }
        self._dump_meta(meta)

    def _dump_meta(self, meta):
        meta_string = json.dumps(meta)
        with open(self.meta_path, 'w') as fp:
            fp.write(meta_string)

    def _load_meta(self):
        with open(self.meta_path) as fp:
            return json.load(fp)

    def _write_text(self, path):
        logger.info('reading pdf: %s' % path)
        text = get_pdf_text(path)

        with open(self.text_path, 'w') as fp:
            fp.write(text)

    def put(self, info):
        mkdir_p(self.path)
        self._write_info_to_meta(info)
        self._write_text(info.path)

    def merge_path(self, path):
        meta = self._load_meta()
        if path not in meta['paths']:
            meta['paths'][path] = now()
            self._dump_meta(meta)
            return 1


class Repo(object):

    def __init__(self, root):
        self.root = os.path.abspath(root)

    def item(self, key):
        path = os.path.join(key[:2], key[2:4], key[4:6], key[6:])
        path = os.path.join(self.root, path)
        return Item(path)

    def exists(self, key):
        return self.item(key).exists()

    def merge_path(self, key, path):
        return self.item(key).merge_path(path)

    def put(self, key, info):
        return self.item(key).put(info)

    def write_queue(self, queue):
        if not queue:
            return
        data = '\n'.join([ ('N %s' % each) for each in queue ])
        fname = os.path.join(self.root, 'queue.%s' % int(time.time()))
        with open(fname, 'w') as fp:
            fp.write(data)
        return fname


def update(repo_path, lib_paths):
    repo = Repo(repo_path)
    queue = []

    for info in head(scan(lib_paths, make_ext_filter('pdf')), n=2):
        key = info.fingerprint
        if repo.exists(key):
            if repo.merge_path(key, info.path):
                logger.info('path updated: %s' % key)
        else:
            repo.put(key, info)
            logger.info('new file added: %s' % key)
            queue.append(key)

    if queue:
        repo.write_queue(queue)


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
