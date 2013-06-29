import os
import json
import argparse

import cherrypy
from mako.lookup import TemplateLookup

from bookworm.seg import search
from bookworm.repo import key_to_path


template_dir = os.path.join(os.path.dirname(__file__), 'template')
lookup = TemplateLookup(directories=[template_dir])


def get_item(match):
    meta = json.loads(match.document.get_data())
    if not meta['paths']:
        return

    key = meta['key']
    docpath = meta['paths'].keys()[0]
    #FIXME: hardcode here
    docpath = os.path.join('files', docpath.split('Documents/ebook/')[1])
    kpath = key_to_path(key)

    item = {
        'rank': match.rank,
        'docid': match.docid,
        'filelink': docpath,
        'title': os.path.splitext(os.path.basename(docpath))[0].replace('.', ' '),
        'key': key,
        }

    thumbpath = os.path.join(kpath, 'thumb.png')
    if os.path.exists(os.path.join(repo_path, thumbpath)):
        item['thumb'] = os.path.join('repo', thumbpath)

    metapath = os.path.join(repo_path, kpath, 'meta')
    if os.path.exists(metapath):
        item['meta'] = json.load(open(metapath))
    return item


class Root(object):

    @cherrypy.expose
    def index(self, q=''):
        tmpl = lookup.get_template('index.html')
        if not q:
            return tmpl.render(q=q)

        result, hits, doccount = [], 0, 0
        querystring = q.encode('utf8') if isinstance(q, unicode) else q
        doccount, mset = search(db_path, querystring, pagesize=30)
        hits = mset.get_matches_estimated()
        for match in mset:
            item = get_item(match)
            if item:
                result.append(item)

        return tmpl.render(q=q,
                           result=result,
                           hits=hits,
                           doccount=doccount)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-path', type=os.path.abspath,
                        default='db', help='path to xapian db')
    parser.add_argument('--repo-path', type=os.path.abspath,
                        default='repo', help='path to repo')
    parser.add_argument('--lib-path', type=os.path.expanduser,
                        default='~/Documents/ebook/',
                        help='path to ebook library')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=8080, type=int)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    db_path = args.db_path
    repo_path = args.repo_path
    lib_path = args.lib_path

    cherrypy.config.update({
            'server.socket_host': args.host,
            'server.socket_port': args.port,
            })

    conf = {'/files': {'tools.staticdir.on': True,
                       'tools.staticdir.dir': lib_path,
                       'tools.staticdir.content_types': {'pdf': 'application/pdf'},
                       },
            '/repo': {'tools.staticdir.on': True,
                      'tools.staticdir.dir': repo_path,
                      'tools.staticdir.content_types': {'pdf': 'application/pdf'},
                      },
            }
    cherrypy.quickstart(Root(), '/', config=conf)
