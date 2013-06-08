import os
import sys
import hashlib
from pprint import pprint

from pyPdf import PdfFileReader as Reader


def human_readable_bytes(num, k=1024.):
    for x in ['bytes','KB','MB','GB']:
        if num < k and num > -k:
            return "%3.1f%s" % (num, x)
        num /= k
    return "%3.1f%s" % (num, 'TB')



class PDF(object):

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self._data = None

    def _get_file_info(self):
        name = os.path.basename(self.path)
        ext = os.path.splitext(name)[1].lstrip(os.path.extsep)
        with open(self.path) as f:
            size = os.fstat(f.fileno()).st_size
            md5 = hashlib.md5(f.read()).hexdigest()
        return {
            'filename': name,
            'path': self.path,
            'ext': ext,
            'size': size,
            'sizeh': human_readable_bytes(size),
            'md5': md5,
            }
        
    def _get_meta(self):
        with open(self.path) as f:
            reader = Reader(f)
            info = reader.getDocumentInfo()
            pages = reader.getNumPages()

        r = {'numpages': pages}
        if info.author:
            r['author'] = info.author
        if info.title:
            r['title'] = info.title
        if info.subject:
            r['subject'] = info.subject
        return r

    def get_data(self):
        if self._data is None:
            self._data = self._get_file_info()
            self._data.update(self._get_meta())
        return self._data

    def get_id(self):
        return self.get_data()['md5']

    def get_content(self):
        with open(self.path) as f:
            reader = Reader(f)
            for i in range(reader.getNumPages()):
                #TODO: add progress bar
                page = reader.getPage(i)
                yield page.extractText()


if __name__ == '__main__':
    pdf = PDF(sys.argv[1])
    pprint(pdf.get_data())
    print pdf.get_id()
    for text in pdf.get_content():
        print text
