#!/usr/bin/env python

from transformers import AutoTokenizer
from difflib import SequenceMatcher

tokenizer = AutoTokenizer.from_pretrained("FacebookAI/xlm-roberta-large")

# Токенізуємо обидва рядки
tokens1 = tokenizer("Белов Степан Сергійович")['input_ids']
tokens2 = tokenizer("Белов Степар Сергійович")['input_ids']

# Обчислюємо LCS подібність
def lcs_similarity(tokens1, tokens2):
    seq_matcher = SequenceMatcher(None, tokens1, tokens2)
    match_ratio = seq_matcher.ratio()  # Відношення LCS до довжини послідовностей
    return match_ratio

similarity = lcs_similarity(tokens1, tokens2)
print(f"LCS Similarity: {similarity}")

