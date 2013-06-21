import os
import sys
import base64
import httplib
import mimetypes


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


if __name__ == '__main__':
    filename = sys.argv[1]
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
