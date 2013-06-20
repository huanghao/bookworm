import os
import sys
import json
import logging
import argparse

import xapian

import guess_language
from repo import Repo
from fingerprint import Fingerprint


logger = logging.getLogger('indexer')


class DB(object):

    def __init__(self, root):
        self.root = root
        self.db = xapian.WritableDatabase(self.root, xapian.DB_CREATE_OR_OPEN)

    def contains(self, key):
        queryparser = xapian.QueryParser()
        queryparser.set_stemmer(xapian.Stem("en"))
        queryparser.set_stemming_strategy(queryparser.STEM_SOME)
        queryparser.add_prefix("key", "Q")

        querystring = "key:%s" % key
        query = queryparser.parse_query(querystring)

        enquire = xapian.Enquire(self.db)
        enquire.set_query(query)

        mset = enquire.get_mset(0, 1)
        return len(mset) > 0

    def put(self, key, item):
        text = item.text
        lang = guess_language.classifier.guess(text[:1024*100])
        logger.debug('lanuage is %s' % lang)
        if lang != 'english':
            logger.warn('language %s is not supported' % lang)
            return

        doc = xapian.Document()
        termgenerator = xapian.TermGenerator()
        termgenerator.set_document(doc)
        termgenerator.set_stemmer(xapian.Stem("en"))
        termgenerator.index_text(text)

        #TODO: add meta info to data
        doc.set_data(json.dumps(item.meta))

        idterm = u"Q" + key
        doc.add_boolean_term(idterm)
        self.db.replace_document(idterm, doc)
        self.db.commit()
        logger.info('index had made %s', idterm)


class Indexer(object):

    def __init__(self, db_path, repo_path):
        self.db = DB(db_path)
        self.repo = Repo(repo_path)

    def index(self, docpath):
        key = Fingerprint(docpath).hex()
        skip = 0

        try:
            ret = self.repo.check(key)
            if ret < 0:
                skip = 1
            elif ret == 0:
                self.repo.put(key, docpath)
            else:
                self.repo.update(key, docpath)

            if not skip:
                item = self.repo.get(key)
        except Exception, err:
            logger.error(str(err))
            skip = 1

        if not skip:
            if self.db.contains(key):
                logger.info('already indexed')
            else:
                
                self.db.put(key, item)


def main(args):
    if not os.path.isdir(args.db_path):
        logger.error('db path does not exist(%s), '
        'please use -d to specify a correct db path' % args.db_path)
        return 1
    if not os.path.isdir(args.repo_path):
        logger.error('repo path does not exist(%s), '
        'please use -r to specify a correct repo path' % args.repo_path)
        return 1

    indexer = Indexer(args.db_path, args.repo_path)
    if args.pdf:
        indexer.index(args.pdf)
        return 0

    input_ = None
    if args.pdf_list_file:
        input_ = open(args.pdf_list_file)
    elif not sys.stdin.isatty():
        input_ = sys.stdin

    if not input_:
        logger.error("can't find any input, please give a pdf file"
        " or use -f to give a list of pdf file")
        return 2

    for line in input_:
        if not line.startswith('#'):
            indexer.index(line.strip())


def parse_args():
    parser = argparse.ArgumentParser(description='''Search repo to index all book
    If there are queue files in root path of repo, it will only deal with those
    queue files. Otherwise it could walk through the whole repo to index them
    all.''')
    parser.add_argument('pdf', nargs='?', help='pdf path to index')
    parser.add_argument('-d', '--db-path', default='db',
        help='xapian db root path')
    parser.add_argument('-r', '--repo-path', default='repo',
        help='ebook repo root path')
    parser.add_argument('-f', '--pdf-list-file', type=os.path.abspath,
        help='given a file each line is a pdf path. '
        'This option conflict with the positional argument "pdf"')
    parser.add_argument('-v', '--verbose',
        action='store_true', help='turn on verbose mode')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, stream=sys.stdout)

    sys.exit(main(args))
