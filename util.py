import os


def head(stream, n=10):
    i = 0
    for each in stream:
        if i < n:
            i += 1
            yield each
        else:
            break


def get_ext(path):
    return os.path.splitext(path)[1].lstrip(os.path.extsep)


def make_ext_filter(wanted):
    '''
    make a filter function which will return true if given path
    in wanted or equals wanted
    '''

    def _filter(path):
        ext = get_ext(path)
        if type(wanted) in (list, tuple):
            return ext in wanted
        return ext == wanted
    return _filter


class ProgressBar(object):

    def __init__(self, total):
        self.total = total
        

    def goto(self, pos):
        
        pass

