import os
import json
import time
import logging

from bookworm.util import Fingerprint, mkdir_p, cd
from bookworm.reader import get_reader

logger = logging.getLogger('repo')


def key_to_path(key):
    return os.path.join(key[:2], key[2:])


class Repo(object):

    def __init__(self, root):
        self.root = os.path.abspath(root)

    def _merge_path(self, oldinfo, newinfo):
        oldpath = set(oldinfo['paths'][:])

        paths = set()
        for path in oldinfo['paths']:
            if os.path.exists(path):
                paths.add(path)
            else:
                logger.info('clean nonexists docpath: %s', path)

        # json.loads return unicode, so convert to unicode to compare
        paths.add(newinfo['paths'][0].decode('utf8'))

        if oldpath == paths:
            return

        oldinfo['paths'] = list(paths)
        return 1

    def _generate_field(self, field, key, method):
        field2filename = {
            'thumbnail': 'thumb.png',
            }

        filename = field2filename.get(field, field)
        err_filename = '{}.err'.format(filename)
        if field != 'info' and os.path.exists(filename) or \
                os.path.exists(err_filename):
            return

        try:
            val = method()
        except Exception as err:
            with open(err_filename, 'w') as fp:
                fp.write(str(err))
            logger.error('error occurs when generate %s for %s: %s',
                         field, key, err)
            return

        if field == 'thumbnail':
            os.rename(val, filename)
            return 1

        if field == 'info':
            val['key'] = key
            if os.path.exists('info'):
                info = json.load(open('info'))
                if not self._merge_path(info, val):
                    return
            val = json.dumps(info)

        with open(filename, 'w') as fp:
            fp.write(val)
        return 1

    def put(self, docpath, search_meta=False):
        key = Fingerprint(docpath).hex()
        docpath = os.path.abspath(docpath)
        changed = 0

        reader_class = get_reader(docpath)
        if not reader_class:
            logger.info('unknown doc type: %s', docpath)
            return changed
        reader = reader_class(docpath)

        itempath = os.path.join(self.root, key_to_path(key))
        if not os.path.exists(itempath):
            mkdir_p(itempath)
            changed += 1

        with cd(itempath):
            for field in reader.fields:
                if self._generate_field(field, key,
                                        lambda:reader.read(field)):
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
