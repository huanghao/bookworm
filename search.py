#!/usr/bin/env python
import os
import sys
import json
import math
import logging
import argparse

import xapian

logger = logging.getLogger(os.path.basename(__file__)[:-3])

def search(dbpath, querystring, offset=0, pagesize=10):
    # offset - defines starting point within result set
    # pagesize - defines number of records to retrieve

    # Open the database we're going to search.
    db = xapian.Database(dbpath)

    # Set up a QueryParser with a stemmer and suitable prefixes
    queryparser = xapian.QueryParser()
    queryparser.set_stemmer(xapian.Stem("en"))
    queryparser.set_stemming_strategy(queryparser.STEM_SOME)
    queryparser.add_prefix("title", "S")
    queryparser.add_prefix("description", "XD")

    # And parse the query
    query = queryparser.parse_query(querystring)

    # Use an Enquire object on the database to run the query
    enquire = xapian.Enquire(db)
    enquire.set_query(query)

    # And print out something about each match
    matches = []
    for match in enquire.get_mset(offset, pagesize):
        matches.append(match.docid)

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
    search(dbpath=args.db_path,
           querystring=' '.join(args.keywords),
           pagesize=args.max_result)
