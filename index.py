import os
import sys
import json
import string
import logging
import argparse

import xapian

import guess_language
from repo import Repo
from fingerprint import Fingerprint
from mmseg.search import seg_txt_search, seg_txt_2_dict


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

        doc = xapian.Document()
        termgenerator = xapian.TermGenerator()
        termgenerator.set_document(doc)
        termgenerator.set_stemmer(xapian.Stem("en"))

        if lang == 'chinese':
            for word, value in seg_txt_2_dict(text).iteritems():
                doc.add_term(word, value)
        else:
            termgenerator.index_text(text)

        transtab = string.maketrans(string.punctuation,
            ' '*len(string.punctuation))
        for path in item.meta['paths']:
            path = path.encode('utf8') # json.loads return unicode
            basepart = os.path.basename(path).split('.')[:-1]
            title = '.'.join(basepart)
            title = title.translate(transtab)
            termgenerator.index_text(title, 1, 'S')
            if guess_language.classifier.guess(title) == 'chinese':
                logger.debug('title lanuage is chinese')
                for word in seg_txt_search(title):
                    doc.add_term(word)
                    doc.add_term('S'+word)

        doc.set_data(json.dumps(item.meta))

        idterm = u"Q" + key
        doc.add_boolean_term(idterm)
        self.db.replace_document(idterm, doc)
        self.db.commit()
        logger.info('index had made %s', idterm)


class Indexer(object):

    def __init__(self, db_path, repo_path, force_index=False):
        self.db = DB(db_path)
        self.repo = Repo(repo_path)
        self.force_index = force_index

    def index(self, docpath):
        key = Fingerprint(docpath).hex()

        try:
            changed = self.repo.put(key, docpath)
            item = self.repo.get(key)
        except Exception, err:
            logger.error(str(err))
        else:
            if self.force_index or \
                changed or \
                not self.db.contains(key):
                self.db.put(key, item)
            else:
                logger.debug('already indexed:%s', docpath)


def main(args):
    if not os.path.isdir(args.db_path):
        logger.error('db path does not exist(%s), '
        'please use -d to specify a correct db path' % args.db_path)
        return 1
    if not os.path.isdir(args.repo_path):
        logger.error('repo path does not exist(%s), '
        'please use -r to specify a correct repo path' % args.repo_path)
        return 1

    indexer = Indexer(args.db_path, args.repo_path, force_index=args.force_index)
    if args.pdf:
        for pdf in args.pdf:
            indexer.index(pdf)
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
    parser.add_argument('pdf', nargs='*', help='pdf path to index')
    parser.add_argument('-d', '--db-path', default='db',
        help='xapian db root path')
    parser.add_argument('-r', '--repo-path', default='repo',
        help='ebook repo root path')
    parser.add_argument('-f', '--pdf-list-file', type=os.path.abspath,
        help='given a file each line is a pdf path. '
        'This option conflict with the positional argument "pdf"')
    parser.add_argument('--force-index', action='store_true',
                        help='force index even if it exists')
    parser.add_argument('-v', '--verbose',
        action='store_true', help='turn on verbose mode')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, stream=sys.stdout)

    sys.exit(main(args))
