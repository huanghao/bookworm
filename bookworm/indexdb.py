import os
import json
import time
import logging

import xapian
from mmseg.search import seg_txt_2_dict

from bookworm.util import cd
from bookworm.seg import guess_keywords, guess_language

logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])


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

        lang = guess_language(text[:1024*100])
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
