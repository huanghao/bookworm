import os
import sys
import json

from search import search

import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup

db_path = os.path.join(os.path.dirname(__file__), 'db')
template_dir = os.path.join(os.path.dirname(__file__), 'template')
lookup = TemplateLookup(directories=[template_dir])


class Root(object):

    @cherrypy.expose
    def index(self, q=''):
        result = []
        if q:
            for match in search(db_path, q, pagesize=50):
                meta = json.loads(match.document.get_data())
                paths = [ (os.path.join('files', path.split('Documents/')[1]),
                           os.path.basename(path))
                          for path in meta['paths'] ]
                item = {
                    'rank': match.rank,
                    'docid': match.docid,
                    'paths': paths,
                    }
                result.append(item)

        tmpl = lookup.get_template('index.html')
        data = dict([ (name,locals().get(name)) for name in ('q', 'result') ])
        return tmpl.render(**data)


if __name__ == '__main__':
    cherrypy.config.update({
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 8080,
            })

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ebook'))
    conf = {'/files': {'tools.staticdir.on': True,
                       'tools.staticdir.dir': path,
                       'tools.staticdir.content_types': {'pdf': 'application/pdf'},
                       },
            }

    cherrypy.quickstart(Root(), '/', config=conf)
