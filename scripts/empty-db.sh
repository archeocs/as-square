#!/bin/sh

spatialite dist/empty-db.sqlite < asquare-init-db.sql
zip -r dist/empty-db.zip dist/empty-db.sqlite
