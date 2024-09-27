#!/usr/bin/env python

import re
from pathlib import Path

import spacy

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


for file in directory_path.iterdir():
    if file.is_file():
        with open(file, 'r', encoding='utf-8') as file:
            plain_text = file.read()
            joined_text = re.sub(r"\n+", ' ', plain_text)
            cleaned_text = clean_text(joined_text)
            print(f"{file.name}\n{'-'*20}\n{cleaned_text}\n")
    # break
