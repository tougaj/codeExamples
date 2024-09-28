#!/usr/bin/env python

import json
from pathlib import Path
from time import time
from typing import Tuple

from langdetect import detect


def get_file_name(doc: Tuple[str, str]):
    lang = detect(doc[1])
    return f"{doc[0]}_{lang}.txt"


with open("local.texts.json", "r", encoding="utf-8") as file:
    data = json.load(file)

docs = data['response']['docs']
list_len = len(docs)
count = 0
tic = time()
for raw_doc in docs:
    doc_id = raw_doc['id']
    doc_text = '. '.join(raw_doc['body'])
    file_name = Path('./texts') / get_file_name((doc_id, doc_text))
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(doc_text)
        count += 1
    if count % 10 == 0:
        print(f"{count} of {list_len} files created")
toc = time()
elapsed = toc-tic


print(f"🏁 {list_len} files created in {elapsed:.2f} seconds")
