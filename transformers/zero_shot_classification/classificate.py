#!/usr/bin/env python

from transformers import pipeline
from time import time

classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")

sequence_to_classify = "НАТО має намір збільшити кількість боєздатних бригад 131. Водночас заплановано вп'ятеро наростити кількість наземних підрозділів ППО."
# candidate_labels = ["politics", "economy", "entertainment", "environment", "war"]
candidate_labels = ["війна", "політика", "економіка", "події", "суспільство"]

tic = time()
output = classifier(sequence_to_classify, candidate_labels, multi_label=True)
toc = time()

print(output["sequence"])
print('-'*50)
for label, score in zip(output["labels"], output["scores"]):
	print(f"{label}:\t{score}")
print('-'*50)
print(f"Classification took {toc-tic:.2f} seconds")
