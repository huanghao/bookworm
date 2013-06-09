import sys
import logging
import argparse

import xapian

from repo import Repo


logger = logging.getLogger('indexer')


def index(dbpath, repopath, opts):
    db = DB(dbpath)
    repo = Repo(repopath)

    for queue in repo.iter_queue():
        while 1:
            item = queue.next()
            if not item:
                break
            try:
                db.index_doc(item.key, item.text_path)
            except Exception as err:
                queue.mark_as_error(str(err))
                logger.error('Failed to index:%s:%s' % (err, item.key))
            else:
                queue.mark_as_done()
                logger.info('%s has been indexed' % item.key)


class DB(object):

    def __init__(self, dbpath):
        self.root = dbpath
        self.db = None

    def _create(self):
        if self.db is None:
            # Create or open the database we're going to be writing to.
            self.db = xapian.WritableDatabase(self.root, xapian.DB_CREATE_OR_OPEN)

    def index_doc(self, key, docpath):
        self._create()

        termgenerator = xapian.TermGenerator()
        termgenerator.set_stemmer(xapian.Stem("en"))

        doc = xapian.Document()
        termgenerator.set_document(doc)

        termgenerator.index_text(open(docpath).read())

        #TODO: add meta info to data
        doc.set_data(docpath)

        idterm = u"Q" + key
        doc.add_boolean_term(idterm)
        self.db.replace_document(idterm, doc)


def parse_args():
    parser = argparse.ArgumentParser(description='''Search repo to index all book
    If there are queue files in root path of repo, it will only deal with those
    queue files. Otherwise it could walk through the whole repo to index them
    all.''')
    parser.add_argument('db_path')
    parser.add_argument('repo_path')
    parser.add_argument('-v', '--verbose', help='turn on verbose mode')
    return parser.parse_args()


if __name__ == '__main__':
    opts = parse_args()

    level = logging.DEBUG if opts.verbose else logging.INFO
    logging.basicConfig(level=level, stream=sys.stdout)

    sys.exit(index(opts.db_path, opts.repo_path, opts))
