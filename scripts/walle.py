import os
import sys
import logging
import argparse

from bookworm.repo import Repo

logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])


def main(args):
    if not os.path.isdir(args.repo_path):
        logger.error('repo path does not exist(%s), '
        'please use -r to specify a correct repo path' % args.repo_path)
        return 1

    repo = Repo(args.repo_path)

    if args.pdf:
        for pdf in args.pdf:
            repo.put(pdf, args.search_google_for_meta)
        return 0

    input_ = None
    if args.pdf_list_file:
        input_ = open(args.pdf_list_file)
    elif not sys.stdin.isatty():
        input_ = sys.stdin

    if not input_:
        logger.error("can't find any input, please give a pdf file"
        " or use -f to give a list of pdf file")
        return 2

    for line in input_:
        if not line.startswith('#'):
            repo.put(line.strip())


def parse_args():
    parser = argparse.ArgumentParser(description='''Computer fingerprint
    for each pdf it meets, read its content, make cover thumb, search
    via google image ''')
    parser.add_argument('pdf', nargs='*', help='pdf path to index')
    parser.add_argument('-r', '--repo-path', default='repo',
        help='ebook repo root path')
    parser.add_argument('-f', '--pdf-list-file', type=os.path.abspath,
        help='given a file each line is a pdf path. '
        'This option conflict with the positional argument "pdf"')
    parser.add_argument('-v', '--verbose',
        action='store_true', help='turn on verbose mode')
    parser.add_argument('--search-google-for-meta', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, stream=sys.stdout)

    sys.exit(main(args))
