#!/bin/bash -x

LOCK_FILENAME=/tmp/bookworm.indexer.lock

if ! /usr/bin/lockfile -r 3 $LOCK_FILENAME; then
    echo "indexer is running, exiting"
    exit 1
fi

source ~/.virtualenvs/bookworm/bin/activate

cd ~/Documents/db

time find ~/Documents/ebook/ -type f -regex '.*\.\(pdf\|doc\|docx\|ppt\|pptx\|chm\)$' | walle.py -v

time index.py -v

rm -f $LOCK_FILENAME
