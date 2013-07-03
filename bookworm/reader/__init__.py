import inspect

from bookworm.util import get_ext
from bookworm.image_search.util import walk_modules


def find_readers():
    def iter_class():
        for module in walk_modules('bookworm.reader'):
            for obj in vars(module).itervalues():
                if inspect.isclass(obj) and \
                        hasattr(obj, 'support_ext') and \
                        callable(getattr(obj, 'read', None)):
                    yield obj

    readers = {}
    for cls in iter_class():
        if isinstance(cls.support_ext, list):
            for ext in cls.support_ext:
                readers[ext] = cls
        else:
            readers[cls.support_ext] = cls
    return readers


EXT2READER = find_readers()
def get_reader(docpath):
    global EXT2READER
    return EXT2READER.get(get_ext(docpath).lower())


__all__ = ['build_reader']
