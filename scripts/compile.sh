#!/bin/sh

mkdir build
PLUGIN_VER="@__PLUGIN_VERSION__@"
TAG=$(git tag --contains HEAD)

echo $TAG

sed "s/@__PLUGIN_VERSION__@/$TAG/" src/__init__.py > build/__init__.py
sed "s/@__PLUGIN_VERSION__@/$TAG/" src/metadata.txt > build/metadata.txt
sed "s/@__PLUGIN_VERSION__@/$TAG/" plugins.xml > build/plugins.xml

cp src/test_*.py build/
cp src/main.py src/layers_manager.py build/
