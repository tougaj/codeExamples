#!/usr/bin/env bash

# bin/solr delete -c faces
# bin/solr create -c faces
# bin/solr config -c faces -p 8983 -action set-user-property -property update.autoCreateFields -value false
# Також може бути використана наступна команда:
# curl -X POST http://localhost:8983/solr/faces/config?commit=true -d '{"set-user-property":{"update.autoCreateFields":"false"}}'
# Фактично в результаті даної команди створюється файл ./server/solr/faces/conf/configoverlay.json з наступним вмістом:
# {"userProps":{"update.autoCreateFields":"false"}

# curl \
# 	-X POST \
# 	-H 'Content-type:application/json' \
# 	--data-binary '{"delete-field-type":{ "name":"face_vector" }}' \
# 	http://localhost:8983/solr/faces/schema
# curl \
# 	-X POST \
# 	-H 'Content-type:application/json' \
# 	--data-binary '{
# 		"add-field-type" : {
# 		"name":"face_vector",
# 		"class":"solr.DenseVectorField",
# 		"vectorDimension":"4096",
# 		"similarityFunction":"euclidean",
# 		"knnAlgorithm":"hnsw",
# 		"hnswMaxConnections":"512",
# 		"hnswBeamWidth":"1024"}}' \
# 	http://localhost:8983/solr/faces/schema

# curl \
# 	-X POST \
# 	-H 'Content-type:application/json' \
# 	--data-binary '{"delete-field": {"name":"face"}}' \
# 	http://localhost:8983/solr/faces/schema
# curl \
# 	-X POST \
# 	-H 'Content-type:application/json' \
# 	--data-binary '{"add-field": {"name":"face", "type":"face_vector", "stored":true, "indexed": true}}' \
# 	http://localhost:8983/solr/faces/schema


# curl -X POST -H 'Content-type:application/json' --data-binary '{"delete": {"query": "*:*"}}' http://localhost:8983/solr/faces/update?commit=true