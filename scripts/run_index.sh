#!/bin/bash -x

LOCK_FILENAME=/tmp/bookworm.indexer.lock

if ! /usr/bin/lockfile -r 3 $LOCK_FILENAME; then
    echo "indexer is running, exiting"
    exit 1
fi

source /home/huanghao/.virtualenvs/bookworm/bin/activate

cd $(dirname $0)

time find /home/huanghao/Documents/ebook/ -name '*.pdf' | python index.py -v

rm -f $LOCK_FILENAME
