from bookworm.util import get_ext, get_file_size


class BasicReader(object):

    def __init__(self, docpath):
        self.docpath = docpath

    @property
    def fields(self):
        for attr in dir(self):
            if attr.startswith('read_'):
                method = getattr(self, attr)
                if callable(method):
                    yield attr[len('read_'):]

    def read(self, field):
        return getattr(self, 'read_%s' % field)()

    def read_info(self):
        ext2format = {
            'doc': 'word',
            'docx': 'word',
            'pdf': 'pdf',
            }
        ext = get_ext(self.docpath)
        fmt = ext2format.get(ext, ext)

        info = {
            'format': fmt,
            'size': get_file_size(self.docpath),
            'paths': [self.docpath],
            }
        return info
