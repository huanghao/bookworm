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

from search import guess_keywords


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

        for path in item.meta['paths']:
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
    if not os.path.isdir(args.repo_path):
        logger.error('repo path does not exist(%s), '
        'please use -r to specify a correct repo path' % args.repo_path)
        return 1

    repo = Repo(args.repo_path)

    if args.pdf:
        for pdf in args.pdf:
            repo.update(docpath)
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
            repo.update(line.strip())


def parse_args():
    parser = argparse.ArgumentParser(description='''Computer fingerprint
    for each pdf it meets, read its content, make cover thumb, search
    via google image ''')
    parser.add_argument('pdf', nargs='*', help='pdf path to index')
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
