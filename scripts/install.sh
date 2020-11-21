#!/bin/sh

NAME=as-square

rm -r ~/.local/share/QGIS/QGIS3/profiles/$NAME/python/plugins/$NAME/
cp -r dist/as-square ~/.local/share/QGIS/QGIS3/profiles/$NAME/python/plugins/$NAME/
