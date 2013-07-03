import os
import logging
import subprocess
import tempfile

from bookworm.reader.basic import BasicReader

logger = logging.getLogger('pdf')


class PdfReader(BasicReader):

    support_ext = 'pdf'

    def read_text(self):
        logger.info('reading pdf content: %s', self.docpath)
        return subprocess.check_output(['pdf2txt.py', self.docpath])

    def read_thumbnail(self):
        fileno, tmp = tempfile.mkstemp(suffix='png')
        os.close(fileno)
        cmd = ['convert', '%s[0]' % self.docpath, tmp]
        subprocess.check_output(cmd)
        return tmp

    def _read_pdf_num_pages(self):
        from pyPdf import PdfFileReader

        logger.info('reading pdf meta: %s', self.docpath)
        reader = PdfFileReader(open(self.docpath, 'rb'))
        return reader.getNumPages()

    def _read_meta(self):
        pass
        #if os.path.exists('thumb.png'):
        #    image_search('thumb.png', 'meta')
