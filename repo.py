import os
import json
import time
import glob
import shutil
import logging
import datetime

from util import mkdir_p, get_ext, get_file_size
from reader import get_pdf_num_pages, get_pdf_text, FailedToRead


logger = logging.getLogger('repo')


def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def key_to_path(key):
    return os.path.join(key[:2], key[2:4], key[4:6], key[6:])

class Repo(object):

    def __init__(self, root):
        self.root = os.path.abspath(root)

    def contains(self, key):
        return os.path.exists(self.meta_path(key))

    def update(self, key, docpath):
        def merge_path(docpath):
            meta = self.load_meta(key)
            # json load string as unicode, in order to compare, change to unicode type first
            upath = docpath if isinstance(docpath, unicode) else docpath.decode('utf8')
            if upath not in meta['paths']:
                meta['paths'][upath] = now()
                self.dump_meta(data)
        merge_path(docpath)

    def put(self, key, docpath):
        docpath = os.path.abspath(docpath)
        mkdir_p(self.key_to_path(key))

        logger.info('reading pdf: %s' % docpath)
        try:
            self.dump_meta(key, {
                'key': key,
                'format': get_ext(docpath),
                'size': get_file_size(docpath),
                'paths': {
                    docpath: now(),
                    },
                'num_pages': get_pdf_num_pages(docpath),
                })

            self.dump_text(key, get_pdf_text(docpath))
        except FailedToRead as err:
            logger.error(err)
            self.mark_as_bad(str(err))

    class Item(object):

        def __init__(self, repo, key):
            self.repo = repo
            self.meta = self.repo.load_meta(key)
            self.text = self.repo.load_text(key)

    def get(self, key):
        return self.Item(self, key)

    #-----------------------------------
    def key_to_path(self, key):
        return os.path.join(self.root, key_to_path(key))

    def meta_path(self, key):
        return os.path.join(self.key_to_path(key), 'meta')

    def load_meta(self, key):
        return json.load(open(self.meta_path(key)))

    def dump_meta(self, key, data):
        with open(self.meta_path(key), 'w') as fp:
            return json.dump(data, fp)

    def text_path(self, key):
        return os.path.join(self.key_to_path(key), 'text')

    def load_text(self, key):
        return open(self.text_path(key)).read()

    def dump_text(self, key, data):
        with open(self.text_path(key), 'w') as fp:
            fp.write(data)

    def mark_as_bad(self, key, reason):
        path = os.path.join(self.key_to_path(key), 'bad')
        with open(path, 'w') as fp:
            fp.write(reason+'\n')
