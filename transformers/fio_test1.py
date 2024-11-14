#!/usr/bin/env python

from transformers import AutoTokenizer, AutoModel
import torch
from scipy.spatial.distance import cosine

# Ініціалізуємо токенайзер і модель
tokenizer = AutoTokenizer.from_pretrained("FacebookAI/xlm-roberta-large")
model = AutoModel.from_pretrained("FacebookAI/xlm-roberta-large")

# Функція для отримання вектора для речення
def get_sentence_vector(sentence):
    inputs = tokenizer(sentence, return_tensors="pt")
    outputs = model(**inputs)
    # Беремо вектори останнього прихованого шару
    last_hidden_state = outputs.last_hidden_state
    # Обчислюємо середнє значення по всім токенам
    sentence_vector = last_hidden_state.mean(dim=1).squeeze().detach().numpy()
    return sentence_vector

# Порівнюємо два речення
sentence1 = "Белов Степан Сергійович"
sentence2 = "Білялетдінов Степар Сергійович"

vec1 = get_sentence_vector(sentence1)
vec2 = get_sentence_vector(sentence2)

# Обчислюємо косинусну подібність
similarity = 1 - cosine(vec1, vec2)
print(f"Cosine similarity: {similarity}")
