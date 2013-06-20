import subprocess

from pyPdf import PdfFileReader


class FailedToRead(Exception):
    '''General Error for reading pdf failed'''


def get_pdf_num_pages(path):
    try:
        reader = PdfFileReader(open(path, 'rb'))
        return reader.getNumPages()
    except Exception as err:
        raise FailedToRead('failed to get pdf num pages:%s:%s' % (err, path))


def get_pdf_text(path):
    try:
        return subprocess.check_output(['pdf2txt.py', path])
    except Exception as err:
        raise FailedToRead('failed to get pdf content:%s:%s' % (err, path))


def make_thumbnail(pdfpath, thumbpath):
    try:
        return subprocess.check_output(['convert', '%s[0]' % pdfpath, thumbpath])
    except Exception as err:
        raise FailedToRead('failed to make thumbnail:%s' % pdfpath)
