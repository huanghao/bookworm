import os


def key_to_path(key):
    return os.path.join(key[:2], key[2:4], key[4:6], key[6:])


#TODO: queueitem and repoitem could be the same thing ?
class QueueItem(object):

    def __init__(self, key, repo_path=None):
        self.key = key
        if repo_path:
            self.text_path = os.path.join(repo_path,
                                          key_to_path(key),
                                          'text')
    def __str__(self):
        return self.key


class QueueReader(object):

    def __init__(self, repo_path, path):
        self.repo_path = repo_path
        self.path = path
        self.current_item = None

    def next(self):
        '''get next item in queue'''
        with open(self.path) as fp:
            line = fp.readline().strip()
            if line:
                self.current_item = QueueItem(line, self.repo_path)
                return self.current_item

    def _remove_the_first_line(self):
        with open(self.path) as fp:
            fp.readline() # skip current line
            content = fp.read()
        with open(self.path, 'w') as fp:
            fp.write(content)

    def mark_as_error(self, reason):
        '''mark current item as error'''
        self._remove_the_first_line()

        error_file = 'index.error.%s' % self.current_item.key
        error_file = os.path.join(os.path.dirname(self.path),
                                  error_file)
        with open(error_file, 'w') as fp:
            fp.write(reason)

    def mark_as_done(self):
        '''mark current item done'''
        self._remove_the_first_line()


class QueueWriter(object):

    def __init__(self, path):
        self.path = path
        self.items = []

    def add(self, item):
        self.items.append(item)

    def save(self):
        if not self.items:
            return

        data = os.linesep.join([ str(item) for item in self.items ])
        with open(self.path, 'w') as fp:
            fp.write(data + os.linesep)
