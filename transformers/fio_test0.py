#!/usr/bin/env python

import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

# Завантажуємо токенайзер та модель
tokenizer = AutoTokenizer.from_pretrained("FacebookAI/xlm-roberta-large")
model = AutoModel.from_pretrained("FacebookAI/xlm-roberta-large")

def get_embedding(text):
    # Токенізуємо текст та передаємо в модель
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    # Отримуємо приховані стани [batch_size, sequence_length, hidden_size]
    hidden_states = outputs.last_hidden_state
    # Усереднюємо всі токени для отримання одного вектора
    mean_embedding = hidden_states.mean(dim=1).squeeze()
    return mean_embedding

# Обчислюємо embeddings для обох текстів
embedding1 = get_embedding("Белов Степан Сергійович")
embedding2 = get_embedding("Белялетдінов Петро Абрамович")

# print(embedding1.shape)

# Обчислюємо косинусну схожість
similarity = cosine_similarity(embedding1.unsqueeze(0), embedding2.unsqueeze(0))

print(f"Схожість між текстами: {similarity[0][0]}")

