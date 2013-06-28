import os
import json

from search import search
from repo import key_to_path

import cherrypy
from mako.lookup import TemplateLookup

db_path = os.path.join(os.path.dirname(__file__), 'db')
repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'repo'))
lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ebook'))

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


if __name__ == '__main__':
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
