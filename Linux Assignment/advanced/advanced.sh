#!/bin/bash
. ./config.cfg


#This is nowhere near finished. One of the issues I've found difficult is configuring the config.cfg file, specifically how to store the queries then how to access/manipulate them.
IFS=";"


echo $query


#for query in $queries; do
#	echo "$query"
#	IFS=':'
#	read -r -a array <<< "$query"
#	echo "${array[2]}"
#	IFS=" "
#	read -r -a ${array[2]} <<< ${array[2]}
#	
#	PGPASSWORD=$password psql -h $dbhost -d $dbname -U $username << EOF
#		
#	EOF
#done

