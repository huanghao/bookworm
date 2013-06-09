import os
import json
import time
import glob
import shutil
import logging
import datetime

from util import mkdir_p
from reader import get_pdf_num_pages, get_pdf_text, FailedToRead
from queue import QueueReader, QueueWriter, key_to_path


logger = logging.getLogger('repo')


def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class RepoItem(object):

    META = 'meta'
    TEXT = 'text'
    MALFORMED = 'malformed'
    MISSING = 'missing'

    class Status(object):
        OK = 1
        DoesNotExist = 0
        Malformed = -1

    def __init__(self, path):
        self.path = path
        self.meta_path = os.path.join(self.path, self.META)
        self.text_path = os.path.join(self.path, self.TEXT)
        self.malformed_path = os.path.join(self.path, self.MALFORMED)

    def check(self):
        if os.path.exists(self.malformed_path):
            return self.Status.Malformed
        if os.path.exists(self.text_path):
            return self.Status.OK
        return self.Status.DoesNotExist

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
        text = get_pdf_text(path)
        with open(self.text_path, 'w') as fp:
            fp.write(text)

    def mark_malformed(self):
        open(self.malformed_path, 'w').close()

    def put(self, info):
        mkdir_p(self.path)
        logger.info('reading pdf: %s' % info.path)
        try:
            self._write_info_to_meta(info)
            self._write_text(info.path)
        except FailedToRead as err:
            logger.error(err)
            self.mark_malformed()
            return
        return 1

    def merge_path(self, path):
        meta = self._load_meta()
        # json load string as unicode, in order to compare, change to unicode type first
        if path.decode('utf8') not in meta['paths']:
            meta['paths'][path] = now()
            self._dump_meta(meta)
            return 1


class Repo(object):

    def __init__(self, root):
        self.root = os.path.abspath(root)

    def item(self, key):
        path = os.path.join(self.root, key_to_path(key))
        return RepoItem(path)

    def check(self, key):
        return self.item(key).check()

    def merge_path(self, key, path):
        return self.item(key).merge_path(path)

    def put(self, key, info):
        return self.item(key).put(info)

    def iter_queue(self):
        running = os.path.join(self.root, 'running')
        while 1:
            files = glob.glob(os.path.join(self.root, 'queue.*'))
            if files:
                shutil.move(files[0], running)
                yield QueueReader(self.root, running)
            else:
                break

    def new_queue(self):
        path = os.path.join(self.root,
                            'queue.%s' % int(time.time()))
        return QueueWriter(path)
