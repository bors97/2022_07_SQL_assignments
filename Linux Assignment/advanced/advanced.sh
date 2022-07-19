#!/bin/sh
. ./config.cfg

echo "$dbhost $dbname"

PGPASSWORD=$password psql -h $dbhost -d $dbname -U $username << EOF

EOF
