#!/usr/bin/env python
import os
import json
import math
import logging
import argparse

import xapian
from mmseg.search import seg_txt_search

logger = logging.getLogger(os.path.basename(__file__)[:-3])


def guess_keywords(querystring, known_prefix=None):
    stem = xapian.Stem('en')
    words = []
    contains_chinese = 0
    for piece in querystring.split():
        prefix = None
        if known_prefix and ':' in piece:
            qprefix, other = piece.split(':', 1)
            if qprefix in known_prefix:
                prefix = known_prefix[qprefix]
                piece = other

        for word in seg_txt_search(piece):
            if ord(word[0]) <= 127: # english
                word = stem(word)
            else:
                contains_chinese = 1
            if prefix:
                words.append(prefix + word)
            else:
                words.append(word)

    return contains_chinese, words


def search(dbpath, querystring, offset=0, pagesize=10):
    # offset - defines starting point within result set
    # pagesize - defines number of records to retrieve
    
    db = xapian.Database(dbpath)

    known_prefix = {
        'title': 'S',
        'description': 'XD',
        'key': 'Q',
        }
    contains_chinese, words = guess_keywords(querystring, known_prefix)
    logger.debug('contains chinese: %d', contains_chinese)
    logger.debug('words: %s', '\n'.join(words))

    if contains_chinese:
        if len(words) == 1:
            query = xapian.Query(words[0])
        else:
            query = xapian.Query(xapian.Query.OP_AND,
                [ xapian.Query(w) for w in words ])
    else:
        queryparser = xapian.QueryParser()
        queryparser.set_stemmer(xapian.Stem("en"))
        queryparser.set_stemming_strategy(queryparser.STEM_SOME)
        for k, v in known_prefix.iteritems():
            queryparser.add_prefix(k, v)
        query = queryparser.parse_query(querystring)

    enquire = xapian.Enquire(db)
    enquire.set_query(query)
    return enquire.get_mset(offset, pagesize)


def print_search(dbpath, querystring, offset=0, pagesize=10):
    for match in search(dbpath, querystring, offset, pagesize):
        meta = json.loads(match.document.get_data())
        logger.info('[%0*d]:%s',
                    int(math.log(pagesize, 10)+1),
                    match.rank + 1,
                    #match.docid,
                    '\n'.join([i.replace('/home/huanghao/Documents/ebook/', '') for i in meta['paths']]))
        logger.debug(json.dumps(meta, indent=4))


def parse_args():
    parser = argparse.ArgumentParser(description='''Search db''')
    parser.add_argument('keywords', nargs='*', help='keywords')
    parser.add_argument('-d', '--db-path', default='db',
                        help='xapian db root path')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='turn on verbose mode')
    parser.add_argument('-n', '--max-result', type=int, default=10,
                        help='max number of result to retrieve')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level)
    print_search(dbpath=args.db_path,
                 querystring=' '.join(args.keywords),
                 pagesize=args.max_result)
