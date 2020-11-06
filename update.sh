#!/bin/sh

NAME=as-square


rm -rv ~/.local/share/QGIS/QGIS3/profiles/$NAME/python/plugins/$NAME/*
cp -v src/* ~/.local/share/QGIS/QGIS3/profiles/$NAME/python/plugins/$NAME/
