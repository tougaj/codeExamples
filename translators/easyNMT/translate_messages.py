#!/usr/bin/env python

import json
import os
from typing import TypedDict

from easynmt import EasyNMT
from tqdm import tqdm
from utils import TextCleaner, detect_language

model = EasyNMT('opus-mt')
# model = EasyNMT('m2m_100_1.2B')


# import nltk
# nltk.download('punkt_tab')


class Message(TypedDict):
    id: str
    source_id: int
    source_title: str
    url: str
    hit_date: str  # ISO-8601 datetime в рядковому форматі
    body_len: int
    country: str
    title: str
    body: str
    author: str
    insert_date: str  # ISO-8601 datetime в рядковому форматі
    language: str
    translated_title: str
    translated_body: str


def process_json_files(directory):
    # Отримання списку файлів у каталозі
    files = [f for f in os.listdir(directory) if f.endswith(".json")]

    # Проходження по файлах з відображенням прогресу
    for file in tqdm(files, desc="Translating"):
        file_path = os.path.join(directory, file)

        try:
            # Читання JSON-даних
            with open(file_path, "r", encoding="utf-8") as f:
                data: Message = json.load(f)

            language, cleaned_body = detect_language(data['body'])
            if language is None or language in ['uk', 'ru']:
                continue

            data['language'] = language.upper()

            cleaned_title = TextCleaner(data['title']).remove_unnecessary_symbols().get_stripped_text()
            data['translated_title'] = model.translate(cleaned_title, target_lang='uk')

            data['translated_body'] = model.translate(cleaned_body, target_lang='uk')

            # Запис оновлених даних назад у файл
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Error processing file {file}: {e}")


# Виклик функції
if __name__ == "__main__":
    # Шлях до каталогу з JSON-файлами
    directory = "local.messages"
    process_json_files(directory)

# sentences = sent_tokenize(text)
# words = word_tokenize(text)

# tic = time()
# result = model.translate(text, target_lang='uk')
# toc = time()
# elapsed = toc-tic
# print('-'*50)
# print(result)
# # for r in result:
# # 	print(r['translation_text'])
# print('-'*50)
# print(f"""{len(sentences)} sentences have been translated {dt.timedelta(seconds=round(toc-tic))} ({(toc-tic)/len(sentences):.2f} sec/sentence)
# {len(words)} words have been translated {dt.timedelta(seconds=round(toc-tic))} ({(toc-tic)/len(words):.2f} sec/word)""")
