#!/bin/sh

spatialite dist/empty-db.sqlite < db/as-square-init-db.sql
zip -r dist/empty-db.zip dist/empty-db.sqlite
