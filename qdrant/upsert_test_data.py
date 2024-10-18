#!/usr/bin/env python

import sys
import uuid
from os import environ as env
from time import sleep, time

import numpy as np
from dotenv import find_dotenv, load_dotenv
from qdrant_client import QdrantClient, models
from tqdm import tqdm

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
rg = np.random.default_rng()

client = QdrantClient(
    url=QDRANT_SERVER,
    api_key=API_KEY,
    timeout=60
)
print(f"Connected to server {QDRANT_SERVER}")

if not client.collection_exists(COLLECTION_NAME):
    result = client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE,
            distance=models.Distance.EUCLID,
            on_disk=True,
            # datatype=models.Datatype.FLOAT16
        ),
        optimizers_config=models.OptimizersConfigDiff(
            indexing_threshold=0,
        ),
    )
    print(f"Collection {COLLECTION_NAME} created")

BATCH_SIZE = 1000

for _ in tqdm(range(1000)):
    current_time = int(time()*1e6)
    # ids = [str(uuid.uuid4()) for i in range(BATCH_SIZE)]
    vectors = rg.random((BATCH_SIZE, VECTOR_SIZE))*10-5
    payloads = [{"realm": "moria", "id": f"moria_id_{current_time}_{i}"}
                for i in range(BATCH_SIZE)]
    ids = [str(uuid.uuid5(NAMESPACE, p['id'])) for p in payloads]

    # client.upsert(
    #     collection_name=COLLECTION_NAME,
    #     points=[
    #         models.PointStruct(
    #             id=str(uuid.uuid4()),
    #             vector=np.random.uniform(-5, 5, VECTOR_SIZE).tolist(),
    #         ),
    #     ],
    # )

    success = False
    while not success:
        try:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=models.Batch(
                    ids=ids, payloads=payloads, vectors=vectors,),
                wait=True,
            )
            success = True
        except Exception as e:
            print(e)
            sleep(5)

print('🏁 Upload completed')
