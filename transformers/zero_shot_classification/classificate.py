#!/usr/bin/env python

from transformers import pipeline
from time import time

model = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
classifier = pipeline("zero-shot-classification", model=model, tokenizer=model)
# classifier = pipeline("zero-shot-classification", model="vicgalle/xlm-roberta-large-xnli-anli")
# classifier = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")

# sequence_to_classify = "НАТО має намір збільшити кількість боєздатних бригад 131. Водночас заплановано вп'ятеро наростити кількість наземних підрозділів ППО."
sequence_to_classify = """
Вплив TikTok на вибори у США
"""
# unwanted_labels = ["politics", "economy", "entertainment", "environment", "war"]
unwanted_labels = [
    "astrology",
    "horoscopes",
    "entertainment",
    "celebrity news",
    "gossip",
    "food",
    "recipes",
    "lifestyle",
    "fashion",
    "sports",
    "viral content",
    "humor",
    "funny stories",
    "internet memes",
    # "travel",      # додай, якщо вважаєш за потрібне
    # "wellness",    # додай, якщо фільтруєш "здоров'я"-лайфхаки
]
desired_labels = [
    "politics",
    "international relations",
    "economy",
    "finance",
    "business",
    "war",
    "military conflict",
    "science",
    "technology",
    "health policy",          # ⚠️ не "health" загалом!
    "public health",
    "climate change",
    "environment",
    "education policy",
    "human rights",
    # "law",
    "crime",
    "disasters",
    # "energy",
    "infrastructure"
]
all_labels = desired_labels + unwanted_labels

tic = time()
result = classifier(sequence_to_classify, all_labels, multi_label=True)
toc = time()

print(result["sequence"])
print('-'*50)
for label, score in zip(result["labels"], result["scores"]):
	print(f"{label}:\t{score}")
print('-'*50)
max_unwanted = max(score for label, score in zip(result["labels"], result["scores"]) if label in unwanted_labels)
max_desired = max(score for label, score in zip(result["labels"], result["scores"]) if label in desired_labels)
# keep_article = max_desired > 0.3 and max_unwanted < 0.8
keep_article = max_desired > 0.8 if max_unwanted > 0.8 else max_desired > 0.3
# keep_article = (max_desired > 0.4) or (max_unwanted < 0.7)
print(f"{"✅" if keep_article else "❌"} Keep article is {keep_article}")
print('-'*50)
print(f"Classification took {toc-tic:.2f} seconds")
