import os


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

