import os
import hashlib
import datetime
from contextlib import contextmanager



def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


@contextmanager
def cd(path):
    ''' Context manager which will switch CWD to the given path, and get back
    when operation is done '''

    oldpath = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(oldpath)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as err:
        if err.errno != 17: #OSError: [Errno 17] File exists
            raise

def head(stream, n=10):
    i = 0
    for each in stream:
        if i < n:
            i += 1
            yield each
        else:
            break

def human_readable_bytes(num, k=1024.):
    for x in ['bytes','KB','MB','GB']:
        if num < k and num > -k:
            return "%3.1f%s" % (num, x)
        num /= k
    return "%3.1f%s" % (num, 'TB')

def get_ext(path):
    return os.path.splitext(path)[1].lstrip(os.path.extsep)

def get_file_size(path_or_file):
    if callable(getattr(path_or_file, 'fileno', None)):
        stat = os.fstat(path_or_file.fileno())
    else:
        stat = os.stat(path_or_file)
    return stat.st_size


class Fingerprint(object):
    '''Fingerprint of a file, which contains information calcuate by
    its file size and md5sum of the first data block
    '''

    def __init__(self, path, block_size=None):
        self.path = path
        self.block_size = block_size or os.statvfs(path).f_bsize
        self.size, self.md5 = None, None

    def calculate(self):
        with open(self.path) as file_:
            sample = file_.read(self.block_size)
            stat = os.fstat(file_.fileno())

        self.size = stat.st_size
        self.md5 = hashlib.md5(sample).hexdigest().lower()
        return self.size, self.md5

    def hex(self):
        if self.size is None:
            self.calculate()
        return '%s%x' % (self.md5, self.size)

    def __str__(self):
        return self.hex()
