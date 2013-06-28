import logging
import subprocess

from pyPdf import PdfFileReader

logger = logging.getLogger('reader')


class FailedToRead(Exception):
    '''General Error for reading pdf failed'''


def get_pdf_num_pages(path):
    logger.info('reading pdf meta: %s', path)
    try:
        reader = PdfFileReader(open(path, 'rb'))
        return reader.getNumPages()
    except Exception as err:
        raise FailedToRead('failed to get pdf num pages:%s:%s' % (err, path))


def get_pdf_text(path):
    logger.info('reading pdf content: %s', path)
    return subprocess.check_output(['pdf2txt.py', path])


def make_thumbnail(pdfpath, thumbpath):
    return subprocess.check_output(['convert', '%s[0]' % pdfpath, thumbpath])
