import os
import sys
import json
import time
import logging
import argparse

import xapian

import guess_language
from mmseg.search import seg_txt_search, seg_txt_2_dict

from repo import Repo, key_to_path
from search import guess_keywords
from util import cd


logger = logging.getLogger('indexer')


class DB(object):

    def __init__(self, root):
        self.root = root
        self.db = xapian.WritableDatabase(self.root, xapian.DB_CREATE_OR_OPEN)

    def get_index_time(self, key):
        query = xapian.Query('Q{}'.format(key))

        enquire = xapian.Enquire(self.db)
        enquire.set_query(query)

        mset = enquire.get_mset(0, 1)
        if len(mset) > 0:
            data = json.loads(mset[0].document.get_data())
            return data['lastindex']

    def put(self, key, itempath):
        doc = xapian.Document()
        termgenerator = xapian.TermGenerator()
        termgenerator.set_document(doc)
        termgenerator.set_stemmer(xapian.Stem("en"))

        with cd(itempath):
            info = json.load(open('info'))
            self._index_info(info, doc, termgenerator)
            self._index_text(doc, termgenerator)

        info['lastindex'] = int(time.time())
        doc.set_data(json.dumps(info))

        idterm = u"Q" + key
        doc.add_boolean_term(idterm)
        self.db.replace_document(idterm, doc)
        self.db.commit()
        logger.info('index had made %s', idterm)

    def _index_info(self, info, doc, termgenerator):
        for path in info['paths']:
            path = path.encode('utf8') # json.loads return unicode
            logger.debug('index title path: %s', path)
            basepart = os.path.basename(path).split('.')[:-1]
            title = '.'.join(basepart)

            contains_chinese, words = guess_keywords(title)
            if contains_chinese:
                logger.debug('title contains chinese')
                for word in words:
                    doc.add_term(word)
                    doc.add_term('S' + word)
                    logger.debug('index title word: %s', word)
            else:
                termgenerator.index_text(title, 1, 'S')

    def _index_text(self, doc, termgenerator):
        try:
            text = open('text').read()
        except IOError as err:
            logger.error(str(err))
            return

        lang = guess_language.classifier.guess(text[:1024*100])
        logger.debug('lanuage is %s' % lang)

        if lang == 'chinese':
            for word, value in seg_txt_2_dict(text).iteritems():
                doc.add_term(word, value)
        else:
            termgenerator.index_text(text)

    def index(self, key, itempath, force=False):
        filename = os.path.join(itempath, 'lastchange')
        try:
            lastchange = int(open(filename).read())
        except IOError as err:
            logger.error(str(err))
            return

        if not force:
            lastindex = self.get_index_time(key)
            if lastindex >= lastchange:
                logger.debug('lastindex(%s) >= lastchange(%s)',
                             lastindex, lastchange)
                return
        self.put(key, itempath)



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
