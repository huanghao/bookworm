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

        #find html -type f -regex '.*\.\(html\|htm\)' -exec cat {} \; | html2text | less
        cmd1 = ['find', 'html',
                '-type', 'f',
                '-regex', r'.*\.\(htm\|html\)',
                '-exec', 'cat', '{}', ';',
                ]
        cmd2 = ['html2text', '-']
        logger.info('reading text from html: %s | %s', ' '.join(cmd1), ' '.join(cmd2))

        p1 = Popen(cmd1, stdout=PIPE)
        p2 = Popen(cmd2, stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close() # Allow p1 to receive a SIGPIPE if p2 exits.
        return p2.communicate()[0]
