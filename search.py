#!/usr/bin/env python
import os
import json
import math
import logging
import argparse

import xapian
from mmseg.search import seg_txt_search

import guess_language

logger = logging.getLogger(os.path.basename(__file__)[:-3])

def search(dbpath, querystring, offset=0, pagesize=10):
    # offset - defines starting point within result set
    # pagesize - defines number of records to retrieve

    db = xapian.Database(dbpath)

    if guess_language.classifier.guess(querystring) == 'chinese':
        query_list = []
        for word in seg_txt_search(querystring):
            query = xapian.Query(word)
            query_list.append(query)
        if len(query_list) != 1:
            query = xapian.Query(xapian.Query.OP_OR, query_list)
        else:
            query = query_list[0]
        #TODO: also need prefix search support in chinese
    else:
        queryparser = xapian.QueryParser()
        queryparser.set_stemmer(xapian.Stem("en"))
        queryparser.set_stemming_strategy(queryparser.STEM_SOME)
        queryparser.add_prefix("title", "S")
        queryparser.add_prefix("description", "XD")
        queryparser.add_prefix("key", "Q")
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
