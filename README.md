bookworm
========

mkdir -p db repo

find ~/Documents/ebook -name '*.pdf' | python -m bookworm.walle -v

python -m bookworm.index -v

python -m bookworm.webapp or

python search.py hack


requirements beside of requirements.txt
=======================================
* catdoc: /usr/bin/catdoc
* imagemagick: /usr/bin/convert

