import sys
import subprocess
from StringIO import StringIO

from pyPdf import PdfFileReader
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter

class PdfReader(object):

    def __init__(self, fname):
        self.fname = fname

    def get_text(self):
        buf = StringIO()
        rsrc = PDFResourceManager()
        device = TextConverter(rsrc, buf, codec='utf-8', laparams=None)
        with open(self.fname, 'rb') as fp:
            process_pdf(rsrc, device, fp, None, maxpages=0)
        device.close()
        buf.seek(0)
        text = buf.read()
        print text
        print type(text)
        return text

def make_file_reader(format):
    if format == 'pdf':
        return PdfReader
    raise Exception('unsupported format:%s' % format)
