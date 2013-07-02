import os
import json
import time
import logging
import datetime

from bookworm.util import Fingerprint, mkdir_p, get_ext, get_file_size, cd
from bookworm.reader import get_pdf_text, make_thumbnail
from bookworm.image_search.search import main as image_search

logger = logging.getLogger('repo')


def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def key_to_path(key):
    return os.path.join(key[:2], key[2:])


class Repo(object):

    def __init__(self, root):
        self.root = os.path.abspath(root)

    def _generate_text(self, key, docpath):
        text = get_pdf_text(docpath)
        with open('text', 'w') as fp:
            fp.write(text)

    def _generate_thumb_png(self, key, docpath):
        make_thumbnail(docpath, 'thumb.png')

    def _update_info(self, key, docpath):
        if os.path.exists('info'):
            info = json.load(open('info'))
            if not self._merge_path(docpath, info):
                return 0
        else:
            info = {
                'key': key,
                'format': get_ext(docpath),
                'size': get_file_size(docpath),
                'paths': {
                    docpath: now(),
                    },
                }
        with open('info', 'w') as fp:
            json.dump(info, fp)
        return 1

    def _merge_path(self, docpath, info):
        changed = 0
        # clean up non-exists path
        for path in info['paths'].keys():
            if not os.path.exists(path):
                info['paths'].pop(path)
                changed += 1
                logger.info('clean non-exists path %s', path.encode('utf8'))

        # json load string as unicode, in order to compare, change to unicode type first
        upath = docpath if isinstance(docpath, unicode) else docpath.decode('utf8')
        if upath not in info['paths']:
            info['paths'][upath] = now()
            changed += 1
        return changed

    def _generate_meta(self, key, docpath):
        if os.path.exists('thumb.png'):
            image_search('thumb.png', 'meta')

    def _generate_field(self, field, key, docpath):
        err_filename = '{}.err'.format(field)
        if os.path.exists(err_filename) or os.path.exists(field):
            return

        method = getattr(self, '_generate_{}'\
                         .format(field.replace('.', '_')))
        try:
            method(key, docpath)
        except Exception as err:
            with open(err_filename, 'w') as fp:
                fp.write(str(err))
            logger.error('error occurs when generate %s for %s: %s',
                         field, key, err)
        else:
            return True

    def put(self, docpath, search_meta=False):
        key = Fingerprint(docpath).hex()
        docpath = os.path.abspath(docpath)

        changed = 0
        itempath = os.path.join(self.root, key_to_path(key))

        if not os.path.exists(itempath):
            mkdir_p(itempath)
            changed += 1

        with cd(itempath):
            changed += self._update_info(key, docpath)
            fields = ['text', 'thumb.png']
            if search_meta:
                fields.append('meta')
            for field in fields:
                if self._generate_field(field, key, docpath):
                    changed += 1

            if changed:
                with open('lastchange', 'w') as fp:
                    fp.write(str(int(time.time())))
                logger.debug('%s: %s -> %s', key, docpath, itempath)

        return changed

    def walk(self):
        def listdir(path):
            for name in os.listdir(path):
                yield name, os.path.join(path, name)

        for name1, dir1 in listdir(self.root):
            for name2, itempath in listdir(dir1):
                key = ''.join([name1, name2])
                yield key, itempath


if __name__ == '__main__':
    print 'mkdir repo2'
    for i in range(256):
        print 'mkdir repo2/%02x' % i
