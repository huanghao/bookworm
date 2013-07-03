import os
import glob
import logging
from subprocess import Popen, PIPE, check_output

from bookworm.reader.basic import BasicReader

logger = logging.getLogger('ms')


class DocReader(BasicReader):

    support_ext = ['doc', 'docx']

    def read_text(self):
        cmd = ['catdoc', self.docpath]
        logger.info('reading doc content: %s', ' '.join(cmd))
        return check_output(cmd)


class PPTReader(BasicReader):

    support_ext = ['ppt', 'pptx']

    def read_text(self):
        cmd = ['catppt', self.docpath]
        logger.info('reading ppt content: %s', ' '.join(cmd))
        return check_output(cmd)


class CHMReader(BasicReader):

    support_ext = 'chm'

    def read_html(self):
        cmd = ['extract_chmLib', self.docpath, 'html']
        logger.info('reading chm content to html: %s', ' '.join(cmd))
        return check_output(cmd)
                

    def read_text(self):
        if not os.path.isdir('html'):
            return

        cmd = ['html2text']
        logger.info('reading text from html: %s', ' '.join(cmd))

        cmd.extend(glob.glob('html/*.htm'))
        cmd.extend(glob.glob('html/*.html'))
        return check_output(cmd)
