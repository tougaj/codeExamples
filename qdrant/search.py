#!/usr/bin/env python

import sys
from os import environ as env
from time import time

import numpy as np
from dotenv import find_dotenv, load_dotenv
from qdrant_client import QdrantClient, models

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

API_KEY = env.get('QDRANT_API_KEY')
# if API_KEY is None:
#     print("You need define Qdrant api-key!")
#     sys.exit(1)
QDRANT_SERVER = env.get('QDRANT_SERVER')
if QDRANT_SERVER is None:
    print("You need define Qdrant server!")
    sys.exit(1)
COLLECTION_NAME = env.get('COLLECTION_NAME')
if COLLECTION_NAME is None:
    print("You need define collection name!")
    sys.exit(1)
rg = np.random.default_rng()

client = QdrantClient(
    url=QDRANT_SERVER,
    api_key=API_KEY,
)
print(f"Connected to server {QDRANT_SERVER}")

vector = (rg.random(512)*10-5).tolist()

tic = time()
hits = client.query_points(
    collection_name=COLLECTION_NAME,
    query=vector,
    limit=5,
    search_params=models.SearchParams(
        hnsw_ef=128,
        quantization=models.QuantizationSearchParams(
            ignore=False,
            rescore=True,
            oversampling=2.0,
        )
    ),
    timeout=300).points
toc = time()


for hit in hits:
    print(hit.payload, "score:", hit.score)
print(f"Search took {toc-tic:.2f} seconds")
