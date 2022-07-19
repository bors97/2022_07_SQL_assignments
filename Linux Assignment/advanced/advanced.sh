#!/bin/bash
. ./config.cfg

IFS=";"

for query in $queries; do
	echo "$query"
	IFS=':'
	read -r -a array <<< "$query"
	echo "${array[2]}"
	IFS=" "
	read -r -a ${array[2]} <<< ${array[2]}
	
	PGPASSWORD=$password psql -h $dbhost -d $dbname -U $username << EOF
		
	EOF
done

