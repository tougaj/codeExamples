#!/usr/bin/env python

import sys
import uuid
from os import environ as env

from dotenv import find_dotenv, load_dotenv
from qdrant_client import QdrantClient, models

VECTOR_SIZE = 512
NAMESPACE = uuid.NAMESPACE_URL  # або створіть свій власний UUID

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

client = QdrantClient(
    url=QDRANT_SERVER,
    api_key=API_KEY,
    timeout=60
)
print(f"Connected to server {QDRANT_SERVER}")

client.update_collection(
    collection_name=COLLECTION_NAME,
    optimizer_config=models.OptimizersConfigDiff(indexing_threshold=20000),
)
