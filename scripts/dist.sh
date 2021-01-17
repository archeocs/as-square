#!/bin/sh

mkdir -p dist/as-square/i18n
cp build/__init__.py build/main.py build/layers_manager.py build/object_dict.py build/items.py build/item_view.py build/input_tab2.py build/metadata.txt build/migration.py build/lang.py dist/as-square/
cp build/plugins.xml dist/
cp build/assquare-migration-db.sql dist/as-square
cp -r build/i18n/*.* dist/as-square/i18n
