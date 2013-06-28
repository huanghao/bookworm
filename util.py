import os
from contextlib import contextmanager


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
