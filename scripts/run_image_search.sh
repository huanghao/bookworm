#!/bin/bash

REPO_PATH=$(pwd)/$(dirname $0)/repo
CODE_PATH=$(pwd)/$(dirname $0)/image_search
SLEEP_TIME=600

cd $CODE_PATH
find $REPO_PATH -name thumb.png | while read IMG; do
    output_filename=$(dirname $IMG)/search_result
    if [ -f $output_filename ]; then
        continue
    fi

    echo searching $IMG ...
    if ! python search.py $IMG -o $output_filename; then
        echo "sleep a long time"
        sleep $SLEEP_TIME
    fi
done
