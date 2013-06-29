import os
import json
import argparse

import cherrypy
from mako.lookup import TemplateLookup

from bookworm.seg import search
from bookworm.repo import key_to_path


template_dir = os.path.join(os.path.dirname(__file__), 'template')
lookup = TemplateLookup(directories=[template_dir])


class Root(object):

    @cherrypy.expose
    def index(self, q=''):
        result = []
        if q:
            querystring = q.encode('utf8') if isinstance(q, unicode) else q
            for match in search(db_path, querystring, pagesize=30):
                meta = json.loads(match.document.get_data())
                if not meta['paths']:
                    continue

                key = meta['key']
                path = meta['paths'].keys()[0]
                #FIXME: hardcode here
                path = os.path.join('files', path.split('Documents/ebook/')[1])

                item = {
                    'rank': match.rank,
                    'docid': match.docid,
                    'filelink': path,
                    'title': os.path.basename(path),
                    'key': key,
                    }

                thumbpath = os.path.join(key_to_path(key), 'thumb.png')
                if os.path.exists(os.path.join(repo_path, thumbpath)):
                    item['thumb'] = os.path.join('repo', thumbpath)

                result.append(item)

        tmpl = lookup.get_template('index.html')
        data = dict([ (name,locals().get(name))
            for name in ('q', 'result') ])
        return tmpl.render(**data)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-path', type=os.path.abspath,
                        default='db', help='path to xapian db')
    parser.add_argument('--repo-path', type=os.path.abspath,
                        default='repo', help='path to repo')
    parser.add_argument('--lib-path', type=os.path.expanduser,
                        default='~/Documents/ebook/',
                        help='path to ebook library')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    db_path = args.db_path
    repo_path = args.repo_path
    lib_path = args.lib_path

    cherrypy.config.update({
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 8080,
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
