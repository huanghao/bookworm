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


class ProgressBar(object):

    def __init__(self, total):
        self.total = total

    def goto(self, pos):
        pass
