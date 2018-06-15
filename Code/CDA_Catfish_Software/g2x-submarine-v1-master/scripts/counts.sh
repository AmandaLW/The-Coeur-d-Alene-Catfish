#!/usr/bin/env bash

for db in $(ls -1 ../app/*.db)
do
	rows=$(sqlite3 "$db" < show-row-count.sh)
	name=$(basename $db)
	echo "row count for $name = $rows"
done
