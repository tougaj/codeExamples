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
           "Content-Type": "application/json", }


def query(payload):
    response = requests.post(API_URL, headers=headers,
                             json=payload, timeout=60)
    return response.json()


text = """Multiple swing states are considering or have passed legislation regulating the use of artificial intelligence in political advertising, a novel medium that is expected to wield growing influence over future elections.
“Deepfakes” (videos, audio recordings, photos, and other content created through AI to impersonate someone without their consent) have raised concerns over their ability to interfere with elections. Such technology has been used to impersonate President Joe Biden and Taylor Swift, for example.
Here’s how battleground states are regulating the use of AI in the political arena.
Swing states considering laws
Pennsylvania, North Carolina, and Ohio are considering legislation that aims to regulate the use of AI in political elections.
Several Pennsylvania state representatives have spearheaded AI bills. These proposals include instituting a task force to study the matter, creating a registry of companies developing AI software, requiring disclosures of any AI content, and banning videos using AI-created deepfakes without permission."""
sentences = sent_tokenize(text)

data = {"inputs": sentences, }
tic = time()
output = query(data)
toc = time()
print(output)
print('-'*50)
print(f"{len(sentences)} sentences have been translated {
      toc-tic:.2f} seconds ({(toc-tic)/len(sentences):.2f} sec/sentence)")
