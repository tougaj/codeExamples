#!/usr/bin/env python

from sentence_transformers import SentenceTransformer
import time
from datetime import timedelta

sentences = ["This is an example sentence", "Each sentence is converted", "Українська назва", "Русское название"]

# model = SentenceTransformer('sentence-transformers/LaBSE')
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

start_time = time.time()
embeddings = model.encode(sentences)
end_time = time.time()

print(embeddings)

elapsed = end_time - start_time
# ⏱️ Виведення результату з емоджі
print(f"⏱️ Час виконання: {str(timedelta(seconds=int(elapsed)))}")

