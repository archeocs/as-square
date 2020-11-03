#!/bin/sh

NAME=asquare


rm -rv ~/.local/share/QGIS/QGIS3/profiles/asquare/python/plugins/$NAME/*
cp -v src/* ~/.local/share/QGIS/QGIS3/profiles/asquare/python/plugins/$NAME/
