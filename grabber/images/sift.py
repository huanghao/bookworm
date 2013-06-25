import os
import sys

from PIL import Image

SIFT_CMD = os.path.expanduser('~/workspace/sources/vlfeat-0.9.16/bin/glnxa64/sift')
size = (128, 128)

def process_image(imagename, resultname, params="--edge-thresh 10 --peak-thresh 5"):
    """ Process an image and save the results in a file. """
    if imagename[-3:] != 'pgm':
        # create a pgm file
        im = Image.open(imagename).convert('L').resize(size)
        im.save('tmp.pgm')
        imagename = 'tmp.pgm'

    cmmd = '{} {} --output={} {}'.format(
        SIFT_CMD, imagename, resultname, params)

    os.system(cmmd)
    print 'processed', imagename, 'to', resultname


if __name__ == '__main__':
    process_image(sys.argv[1], sys.argv[2])
