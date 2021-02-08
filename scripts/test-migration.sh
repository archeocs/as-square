#!/bin/sh

spatialite build/test-migration-db.sqlite < db/as-square-db-v1.sql
MIG="x$(spatialite -bail build/test-migration-db.sqlite < db/as-square-migration-db.sql)"
if [ "$MIG" == "x" ]; then
    echo $MIG
		exit 1;
fi
