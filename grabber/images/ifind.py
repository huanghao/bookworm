import csv
import sys
import glob
from PIL import Image

def write_sample():

    size = (128,128)

    def get_data(filename):
        im = Image.open(filename).convert('1')
        im = im.resize(size)
        #im.thumbnail(size)
        return im.getdata()

    with open('sample', 'w') as fp:
        writer = csv.writer(fp)

        data = ['thumb.png'] + list(get_data('thumb.png'))
        writer.writerow(data)

        for img in glob.glob('s*.jpg'):
            data = [img] + list(get_data(img))
            writer.writerow(data)

def nearest():
    def dist(x, y):
        return sum(int(x[i] != y[i]) for i in range(len(x)))

    reader = csv.reader(open('sample'))
    x0 = map(int, reader.next()[1:])
    rows = [ row for row in reader ]
    labels = [ row[0] for row in rows ]
    xs = [ map(int, row[1:]) for row in rows ]
    dists = [ dist(x0, x) for x in xs ]
    mind = sys.maxint
    mini = None
    for i, d in enumerate(dists):
        if d < mind:
            mind = d
            mini = i

    print mind
    print labels[mini]
    Image.open(labels[mini]).show()


#write_sample()
nearest()
