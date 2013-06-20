import os
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
            for match in search(db_path, q):
                item = {
                    'rank': match.rank,
                    'docid': match.docid,
                    }
                item.update(json.loads(match.document.get_data()))
                result.append(item)

        tmpl = lookup.get_template('index.html')
        data = dict([ (name,locals().get(name)) for name in ('q', 'result') ])
        return tmpl.render(**data)


if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            'server.socket_port': 8080,
                           })
    cherrypy.quickstart(Root())
