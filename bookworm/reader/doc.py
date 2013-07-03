import logging
import subprocess

from bookworm.reader.basic import BasicReader

logger = logging.getLogger('doc')


class DocReader(BasicReader):

    support_ext = ['doc', 'docx']

    def read_text(self):
        logger.info('reading doc content: %s', self.docpath)
        return subprocess.check_output(['catdoc', self.docpath])


class PPTReader(BasicReader):

    support_ext = ['ppt', 'pptx']

    def read_text(self):
        logger.info('reading ppt content: %s', self.docpath)
        return subprocess.check_output(['catppt', self.docpath])
