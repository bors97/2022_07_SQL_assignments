#!/bin/bash
. ./config.cfg

for i in "${!queries[@]}"
do
PGPASSWORD=$password psql -h $dbhost -d $dbname -U $username <<EOF
	\copy (${queries[$i]}) to '${directory}/query_${i}.csv' with CSV HEADER;
EOF
gzip "query_${i}.csv"
 done
