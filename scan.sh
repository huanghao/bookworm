#!/usr/bin/env bash

# If there are multi libs, separated by ':'
LIB_PATHS=~/Documents/ebook

echo "$LIB_PATHS" | xargs -n1 -d':' | while read LIB; do
    [ -z "$LIB" ] && continue

    find $LIB -name '*.pdf' -exec md5sum {} \; | sed -e 's/^\\//'
done
