import db
from util import make_ext_filter, head
from scan import scan


LIBS = ['~/Documents/ebook']


def diff(left, right):
    '''
    assume they are already sorted
    '''
    left_len = len(left)
    right_len = len(right)

    left_only = []
    right_only = []

    l, r = 0, 0
    while l < left_len and r < right_len:
        if left[l] == right[r]:
            l += 1
            r += 1
        elif left[l] < right[r]:
            left_only.append(left[l])
            l += 1
        else:
            right_only.append(right[r])
            r += 1

    if l >= left_len:
        while r < right_len:
            right_only.append(right[r])
            r += 1
    else:
        while l < left_len:
            left_only.append(left[l])
            l += 1

    return left_only, right_only


def main():
    fslist = head(scan(LIBS, make_ext_filter('pdf')), n=1)
    fslist = sorted(fslist, key=lambda fdata: fdata.path)

    dblist = db.api.get_paths().all()
    dblist = sorted(dblist, key=lambda path_obj: path_obj.path)
    #TODO: make faster, is there some distributed way to do this

    new, delete = diff(fslist, dblist)
    print len(new)
    print len(delete)

    db.api.add_filedata(new)


if __name__ == '__main__':
    main()
