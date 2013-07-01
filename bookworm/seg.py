#coding: utf8
import os
import zlib
import logging

import xapian
from mmseg.search import seg_txt_search

logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])


def search(dbpath, querystring, offset=0, pagesize=10):
    # offset - defines starting point within result set
    # pagesize - defines number of records to retrieve
    db = xapian.Database(dbpath)
    doccount = db.get_doccount()

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
    mset = enquire.get_mset(offset, pagesize)
    return doccount, mset


def guess_keywords(querystring, known_prefix=None):
    stem = xapian.Stem('en')
    words = set()
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
                words.add(prefix + word)
            else:
                words.add(word)

    return contains_chinese, list(words)


class Entropy:

    def __init__(self):
        self.entro = []

    def register(self, name, corpus):
        """
        register a text as corpus for a language or author.
        <name> may also be a function or whatever you need
        to handle the result.
        """
        corpus = str(corpus)
        ziplen = len(zlib.compress(corpus))
        self.entro.append((name, corpus, ziplen))

    def guess(self, part):
        """
        <part> is a text that will be compared with the registered
        corpora and the function will return what you defined as
        <name> in the registration process.
        """
        what = None
        diff = 0
        part = str(part)
        for name, corpus, ziplen in self.entro:
            nz = len(zlib.compress(corpus + part)) - ziplen
            # print name, nz, ziplen, nz-ziplen, (1.0 * (nz-ziplen)) / len(part)
            if diff==0 or nz<diff:
                what = name
            diff = nz
        return what


classifier = Entropy()

classifier.register("english","""
If you ever wrote a large shell script, you probably know this feeling:
you'd love to add yet another feature, but it's already so slow, and so
big, and so complicated; or the feature involves a system call or other
function that is only accessible from C ...Usually the problem at hand
isn't serious enough to warrant rewriting the script in C; perhaps the
problem requires variable-length strings or other data types (like sorted
lists of file names) that are easy in the shell but lots of work to
implement in C, or perhaps you're not sufficiently familiar with C.
""")

classifier.register("chinese","""
本报美国安纳伯格庄园６月７日电 国家主席习近平７日在美国加利福尼亚州安纳
伯格庄园同美国总统奥巴马举行中美元首第一场会晤。会晤结束后，两国元首共
同会见记者。
　　习近平表示，刚才，我同奥巴马总统进行了第一场会晤，就各自国家的内外政策、
中美新型大国关系以及共同关心的重大国际和地区问题坦诚深入交换意见，并达成
重要共识。
　　习近平表示，我明确告诉奥巴马总统，中国将坚定不移走和平发展道路，坚定不移
深化改革、扩大开放，努力实现中华民族伟大复兴的中国梦，努力促进人类和平与
发展的崇高事业。
　　中国梦要实现国家富强、民族复兴、人民幸福，是和平、发展、合作、共赢的梦，
与包括美国梦在内的世界各国人民的美好梦想相通。
　　习近平强调，我和奥巴马总统都认为，面对经济全球化迅速发展和各国同舟共济的
客观需求，中美应该也可以走出一条不同于历史上大国冲突对抗的新路。双方同意，
共同努力构建新型大国关系，相互尊重，合作共赢，造福两国人民和世界人民。
国际社会也期待中美关系能够不断改善和发展。中美两国合作好了，就可以做世界
稳定的压舱石、世界和平的助推器。
""")

def guess_language(text):
    return classifier.guess(text)


if __name__=="__main__":
    import sys

    for name in sys.stdin:
        name = name.rstrip()
        text = open(name).read(1024)
        print classifier.guess(text), name
        print text[:10].strip()
