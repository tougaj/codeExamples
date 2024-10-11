#!/usr/bin/env python

import os
import sys
from time import time

import requests
from nltk.tokenize import sent_tokenize

API_TOKEN = os.getenv("HF_INFERENCE_API_TOKEN")
if API_TOKEN is None:
    print("You need Authorization Token!")
    sys.exit(1)

API_URL = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-uk"
headers = {"Authorization": f"Bearer {API_TOKEN}",
           "Content-Type": "application/json",
           "x-wait-for-model": "true", }


def query(payload):
    response = requests.post(API_URL, headers=headers,
                             json=payload, timeout=60)
    return response.json()


text = """Since Kamala Harris launched her presidential campaign in late July, fracking has taken on renewed political prominence, particularly given the vice president’s wavering stances and the administration’s efforts to restrict drilling for oil and gas.
While the vice president and Democratic nominee has vowed not to ban the drilling technology, her stance on fracking, also known as hydraulic fracturing, has changed in recent years. Previously, Harris backed doing away with the technology altogether, while President Joe Biden ran for office aiming to stop new oil and gas drilling on federal lands by halting new leases."""
sentences = sent_tokenize(text)

data = {"inputs": sentences, }
tic = time()
output = query(data)
toc = time()
if 'error' in output:
    print(output)
    sys.exit(0)
for sentence in output:
    print(sentence['translation_text'])
print('-'*50)
print(f"{len(sentences)} sentences have been translated "
      f"{toc-tic:.2f} seconds ({(toc-tic)/len(sentences):.2f} sec/sentence)")
