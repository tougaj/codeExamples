#!/usr/bin/env python

# import re
import re
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
        if token.is_stop or token.pos_ == 'SPACE':
            continue
        if token.pos_ != 'PUNCT':
            result += ' '
        result += token.lemma_
    return result.strip()


tic = time()
count = 0
with open('local.corpus.txt', 'w', encoding='utf-8') as result_file:
    for file in directory_path.iterdir():
        if file.is_file():
            with open(file, 'r', encoding='utf-8') as file:
                plain_text = file.read()
                if detect(plain_text) != 'uk':
                    continue
                joined_text = re.sub(
                    r"‹[^›]+›", "", ' '.join(plain_text.split("\n")))
                cleaned_text = clean_text(joined_text)
                result_file.write(cleaned_text+"\n")
                # print(cleaned_text)
                count += 1
                if count % 10 == 0:
                    print(f"{count} files processed")
                # print(f"{file.name}\n{'-'*20}\n{cleaned_text}\n")
        # break
toc = time()
elapsed = toc-tic
print(f"🏁 {count} files processed in {
      elapsed:.2f} seconds ({elapsed/count:.3f} sec per article)")
