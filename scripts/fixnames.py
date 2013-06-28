import os
import re
import sys
import argparse
import logging


logger = logging.getLogger(os.path.basename(__file__))
old_logger = logging.getLogger('OLD')
new_logger = logging.getLogger('NEW')


def walk(top, filter_=None):
    '''give a top dir, yield all files with its path and name
    if filter_ is given, only yield file which pass filter_(name)
    '''
    for dirpath, dirnames, filenames in os.walk(top):
        for name in filenames:
            if filter_ is None or filter_(name):
                yield dirpath, name


def safe_rename(old, new, real_do=False):
    old_logger.info(os.path.basename(old))
    new_logger.info(os.path.basename(new))

    if real_do:
        if os.path.exists(new):
            logger.error('target already exists, don\'t overwrite: %s', new)
            return
        os.rename(old, new)

def replace_chinese_punctuations_to_english(s):
    pass

# re.M is required, \n can be included in file name
UNUSUAL = re.compile(r'[:"$%/;=@`\*\<\>\?\\\^\{\|\}\s]+', re.M)
def replace_unusual_chars_to_a_single_dot(s):
    return UNUSUAL.sub('.', s)

DELIMITER = re.compile(r'[_,\s\.]{2,}', re.M)
def shrink_delimiters(s):
    return DELIMITER.sub('.', s)

# NOTES:
# keep ' (who's)
# keep + (C++)
# keep # (C#)
# keep ! (especially at the begining)
# keep ~ (which may be backup file for emacs)


def main(args):
    oldlist, newlist = [], []

    for dirpath, oldname in walk(args.top):
        name = oldname

        # hyphen is not allowed in Windows
        name = name.replace('-', '_')

        # change & to and
        name = name.replace('&amp;', ' and ')
        name = name.replace('&', ' and ')

        name = replace_unusual_chars_to_a_single_dot(name)
        name = shrink_delimiters(name)

        # change to lower case pdf file name extension
        ext = name[-4:]
        if ext.lower() == '.pdf' and ext != '.pdf':
            name = '%s.pdf' % name[:-4]

        if name != oldname:
            old = os.path.join(dirpath, oldname)
            new = os.path.join(dirpath, name)
            safe_rename(old, new, args.real)
            if args.diff:
                oldlist.append(old)
                newlist.append(new)

    if args.diff and oldlist and newlist:
        oldlist_filename = '%s.old' % args.diff
        newlist_filename = '%s.new' % args.diff
        with open(oldlist_filename, 'w') as fp:
            fp.write('\n'.join(oldlist))
        with open(newlist_filename, 'w') as fp:
            fp.write('\n'.join(newlist))
        logger.info('you can compare these two files to see more detail:\ndiff %s %s',
                    oldlist_filename, newlist_filename)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('top', type=os.path.abspath,
                        help='fix file names in this path')
    parser.add_argument('--real', action='store_true',
                        help='without it, only dry run')
    parser.add_argument('--diff',
                        help='generate two files for diff')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    #level = logging.DEBUG if args.verbose else logging.INFO
    level = logging.INFO
    logging.basicConfig(level=level, stream=sys.stdout)

    main(args)
