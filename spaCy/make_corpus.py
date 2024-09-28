#!/usr/bin/env python

# import re
from pathlib import Path
from time import time

import spacy
from langdetect import detect

directory_path = Path('./texts')

nlp = spacy.load("uk_core_news_lg")


def clean_text(text: str):
    doc = nlp(text)
    result = ''
    for token in doc:
        if token.is_stop:
            continue
        if token.pos_ != 'PUNCT':
            result += ' '
        result += token.lemma_
    return result.strip()


tic = time()
count = 0
for file in directory_path.iterdir():
    if file.is_file():
        with open(file, 'r', encoding='utf-8') as file:
            plain_text = file.read()
            if detect(plain_text) != 'uk':
                continue
            joined_text = ' '.join(plain_text.split("\n"))
            cleaned_text = clean_text(joined_text)
            print(cleaned_text)
            count += 1
            # print(f"{file.name}\n{'-'*20}\n{cleaned_text}\n")
    # break
toc = time()
elapsed = toc-tic
# print(f"🏁 Elapsed time {elapsed:.2f} ({elapsed/count:.3f} sec per article)")
