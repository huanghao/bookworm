#!/bin/bash

sub=$1
lib_path=~/Documents/ebook

if [ -z "$sub" ]; then
    find $lib_path -type f | awk -F'.' '{print $NF}' | sort | uniq -c | sort -k1,1 -n
else
    find $lib_path -type f -name \*.$sub | sort
fi

exit 0
find ~/Documents/ebook/ -type f -regex '.*\.\(pdf\|doc\|docx\)$' | awk -F'.' '{print $NF}' | sort | uniq -c
    354 doc
     19 docx
   2779 pdf

