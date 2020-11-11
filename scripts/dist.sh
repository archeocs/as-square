#!/bin/sh

mkdir -p dist/as-square
cp build/__init__.py build/main.py build/layers_manager.py build/metadata.txt dist/as-square/
cp build/plugins.xml dist/
