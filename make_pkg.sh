#!/bin/sh

rm -r dist
mkdir -p dist/as-square
cp src/__init__.py src/main.py src/layers_manager.py src/metadata.txt dist/as-square/

cd dist

zip -r as-square.zip as-square

cd ..

