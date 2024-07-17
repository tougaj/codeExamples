#!/usr/bin/env bash

curl \
	-X POST \
	-H 'Content-type:application/json' \
	http://localhost:8983/solr/faces/update/json/docs?commit=true \
	--data-binary @../test.json
