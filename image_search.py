import os
import sys
import base64
import random
import httplib
import urlparse
import mimetypes

import requests
import requests_cache
requests_cache.install_cache('cache')

from pyquery import PyQuery as pq


def post_multipart(host, selector, fields, files):
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()

def encode_multipart_formdata(fields, files):
    LIMIT = '----------lImIt_of_THE_fIle_eW_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + LIMIT)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + LIMIT)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + LIMIT + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % LIMIT
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'



def search_by_image_using_stdlib(filename):
    #encoded_file_content = base64.encodestring(open(filename).read())
    encoded_file_content = open(filename).read()

    host = 'images.google.com'
    selector = '/searchbyimage/upload'
    fields = [
        ('image_content', ''),
        ]
    files = [
        ('encoded_image', os.path.basename(filename), encoded_file_content),
        ]

    content_type, body = encode_multipart_formdata(fields, files)
    #print content_type, '\n', body[:500], '\n', '-'*40
    print post_multipart(host, selector, fields, files)


def search_by_image(filename):
    url = 'http://images.google.com/searchbyimage/upload'
    data = {'image_content': ''}
    files = {'encoded_image': open(filename, 'rb')}
    r = requests.post(url, data=data, files=files, allow_redirects=False)
    url = r.headers.get('location')
#    print r.headers
#    print r.history
#    print r.text
    print 'location:', url
    get_best_guess(url)

USER_AGENTS = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',
    'Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'
    )

def urlopen(url):
    return requests.get(url, headers={'User-Agent': random.choice(USER_AGENTS)})

def get_best_guess(url):
    parts = urlparse.urlsplit(url)
    host = '%s://%s' % (parts.scheme, parts.netloc)

    r = urlopen(url)
    html = pq(r.content)

    def show_links(html):
        for link in html('.r')('a'):
            print '* %s: %s' % (link.text, link.attrib['href'])

    print '-'*40
    print 'urls searched by image'
    show_links(html)

    best_guess = html('#topstuff')('div')('a')[-1]
    url = urlparse.urljoin(host, '%s&%s' % (best_guess.attrib['href'], 'as_sitesearch=amazon.com'))
    print '-'*40
    print 'best guess: %s: %s' % (best_guess.text, url)

    r = urlopen(url)
    html = pq(r.content)
    show_links(html)

    
if __name__ == '__main__':
    filename = sys.argv[1]
    search_by_image(filename)
