import os
import json
import logging
import datetime

from util import mkdir_p, get_ext, get_file_size
from reader import get_pdf_num_pages, get_pdf_text, FailedToRead, make_thumbnail


logger = logging.getLogger('repo')


def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def key_to_path(key):
    return os.path.join(key[:2], key[2:4], key[4:6], key[6:])

class Repo(object):

    def __init__(self, root):
        self.root = os.path.abspath(root)

    def _put_meta(self, key, docpath):
        meta = {
            'key': key,
            'format': get_ext(docpath),
            'size': get_file_size(docpath),
            'paths': {
                docpath: now(),
                },
            }
        try:
            meta['num_pages'] = get_pdf_num_pages(docpath)
        except Exception, err:
            logger.error(str(err))
        self.dump_meta(key, meta)

    def _merge_path(self, key, docpath):
        meta = self.load_meta(key)
        changed = 0
        # clean up non-exists path
        for path in meta['paths'].keys():
            print path
            if not os.path.exists(path):
                meta['paths'].pop(path)
                changed += 1
                logger.info('clean non-exists path %s', path.encode('utf8'))

        # json load string as unicode, in order to compare, change to unicode type first
        upath = docpath if isinstance(docpath, unicode) else docpath.decode('utf8')
        if upath not in meta['paths']:
            meta['paths'][upath] = now()
            changed += 1
            logger.info('append path to repo item %s', key)

        if changed:
            self.dump_meta(key, meta)
        return changed

    def _put_text(self, key, docpath):
        self.dump_text(key, get_pdf_text(docpath))

    def _put_thumbnail(self, key, docpath):
        make_thumbnail(docpath, self.thumb_path(key))

    def put(self, key, docpath):
        changed = 0
        if self.is_bad(key):
            return changed

        docpath = os.path.abspath(docpath)
        itempath = self.key_to_path(key)
        if not os.path.exists(itempath):
            mkdir_p(itempath)
            changed += 1
        
        try:
            if os.path.exists(self.meta_path(key)):
                changed += self._merge_path(key, docpath)
            else:
                self._put_meta(key, docpath)
                changed += 1
            if not os.path.exists(self.text_path(key)):
                self._put_text(key, docpath)
                changed += 1
            if not os.path.exists(self.thumb_path(key)):
                self._put_thumbnail(key, docpath)
                changed += 1
        except FailedToRead as err:
            logger.error(err)
            self.mark_as_bad(key, str(err))
            raise

        if changed:
            logger.info('update %s -> %s' % (docpath, itempath))
        return changed

    class Item(object):

        def __init__(self, repo, key):
            self.repo = repo
            self.meta = self.repo.load_meta(key)
            if os.path.exists(self.repo.text_path(key)):
                self.text = self.repo.load_text(key)
            else:
                self.text = ''

    def get(self, key):
        return self.Item(self, key)

    #-----------------------------------
    def key_to_path(self, key):
        return os.path.join(self.root, key_to_path(key))

    def meta_path(self, key):
        return os.path.join(self.key_to_path(key), 'meta')

    def text_path(self, key):
        return os.path.join(self.key_to_path(key), 'text')

    def bad_path(self, key):
        return os.path.join(self.key_to_path(key), 'bad')

    def thumb_path(self, key):
        return os.path.join(self.key_to_path(key), 'thumb.png')

    #-----------------------------------
    def load_meta(self, key):
        return json.load(open(self.meta_path(key)))

    def dump_meta(self, key, data):
        with open(self.meta_path(key), 'w') as fp:
            return json.dump(data, fp)

    def load_text(self, key):
        return open(self.text_path(key)).read()

    def dump_text(self, key, data):
        with open(self.text_path(key), 'w') as fp:
            fp.write(data)

    def mark_as_bad(self, key, reason):
        path = os.path.join(self.key_to_path(key), 'bad')
        with open(path, 'w') as fp:
            fp.write(reason+'\n')

    def is_bad(self, key):
        return os.path.exists(self.bad_path(key))
