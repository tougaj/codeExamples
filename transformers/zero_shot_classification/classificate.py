#!/usr/bin/env python

from transformers import pipeline
from time import time
import sys
from pprint import pprint

model = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
classifier = pipeline("zero-shot-classification", model=model, tokenizer=model)
# classifier = pipeline("zero-shot-classification", model="vicgalle/xlm-roberta-large-xnli-anli")
# classifier = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")

# sequence_to_classify = "НАТО має намір збільшити кількість боєздатних бригад 131. Водночас заплановано вп'ятеро наростити кількість наземних підрозділів ППО."
sequence_to_classify = """
Київ отримає 85 сучасних автобусів та 8 трамваїв, частина вже вийшла на маршрути, - Кличко

В рамках угоди з Європейським інвестиційним банком за Проєктом "Міський громадський транспорт України" Київ отримає 85 сучасних автобусів. 20 з них вже вийшли на маршрути міста.

Як пише РБК-Україна, про це повідомив мер Києва Віталій Кличко.

"Столиця продовжує оновлення рухомого складу громадського транспорту. Навіть у такі складні часи місто дбає про комфорт мешканців", - зазначив Віталій Кличко.
"""
desired_labels = [
    "politics",
    "international relations",
    "economy",
    "finance",
    "business",
    "war",
    "military conflicts",
    "science",
    "technology",
    "health policy",
    "public health",
    "climate change",
    # "environment",
    "environmental issues",
    "education policy",
    "human rights",
    "crime",
    # "disasters",
    "infrastructure",
    "power industry",
    "energy sector",
    "sports politics",          # ⚡ додано
    "legal affairs",            # ⚡ додано
    "court decisions",          # ⚡ додано
    "social issues",            # ⚡ додано
    "cybersecurity",            # ⚡ додано
]
unwanted_labels = [
    "astrology",
    "horoscopes",
    "entertainment",
    "celebrity news",
    "gossip",
    # "food",
    "recipes",
    "lifestyle",
    "fashion",
    # "style",
    "sports",                   # загальний спорт (результати матчів)
    "viral content",
    "humor",
    "funny stories",
    "internet memes",
    "beauty tips",              # ⚡ додано
    "relationship advice",      # ⚡ додано
]
all_labels = desired_labels + unwanted_labels

# tic = time()
# sequences = [sequence_to_classify] * 10
# results = classifier(sequences, all_labels, multi_label=True)
# toc = time()
# pprint(results)
# print('-'*50)
# print(f"Classification took {toc-tic:.2f} seconds")
# sys.exit()

tic = time()
result = classifier(sequence_to_classify, all_labels, multi_label=True)
toc = time()

print(result["sequence"])
print('-'*50)
for label, score in list(zip(result["labels"], result["scores"]))[:15]:
    print(f"{label}:\t{score:.3f}")
print('-'*50)
# 1 варіант (мій)
# max_unwanted = max(score for label, score in zip(result["labels"], result["scores"]) if label in unwanted_labels)
# max_desired = max(score for label, score in zip(result["labels"], result["scores"]) if label in desired_labels)
# # keep_article = max_desired > 0.3 and max_unwanted < 0.8
# keep_article = max_desired > 0.8 if max_unwanted > 0.8 else max_desired > 0.3
# # keep_article = (max_desired > 0.4) or (max_unwanted < 0.7)

# 2 варіант. Враїовується лише одне максимальне значення
# Розрахунок максимальних скорів
# max_unwanted = max((score for label, score in zip(resultґ["labels"], result["scores"]) 
#                     if label in unwanted_labels), default=0)
# max_desired = max((score for label, score in zip(result["labels"], result["scores"]) 
#                    if label in desired_labels), default=0)

# # Логіка фільтрації
# if max_unwanted > 0.95 and max_unwanted > max_desired + 0.03:
#     # Явне домінування розваг (різниця > 3%)
#     keep_article = False
# elif max_desired > 0.70 and (max_unwanted - max_desired) < 0.05:
#     # Сильна серйозна складова, unwanted не домінує
#     keep_article = True
# elif max_unwanted > 0.90 and max_desired < 0.60:
#     # Явні розваги без серйозності
#     keep_article = False
# else:
#     # Сіра зона: desired має бути достатньо високим і конкурентним
#     keep_article = max_desired > 0.45 and max_desired >= max_unwanted * 0.90

# 3 варіант. Враховуються декілька значень з топів в бажаних і небажаних рубриках
# Отримуємо топ-5 скорів
# desired_scores = sorted([score for label, score in zip(result["labels"], result["scores"]) 
#                          if label in desired_labels], reverse=True)
# unwanted_scores = sorted([score for label, score in zip(result["labels"], result["scores"]) 
#                           if label in unwanted_labels], reverse=True)

# # Максимуми
# max_desired = desired_scores[0] if desired_scores else 0
# max_unwanted = unwanted_scores[0] if unwanted_scores else 0

# # Середні топ-5
# TOP_N = 5
# avg_desired = sum(desired_scores[:TOP_N]) / min(len(desired_scores), TOP_N) if desired_scores else 0
# avg_unwanted = sum(unwanted_scores[:TOP_N]) / min(len(unwanted_scores), TOP_N) if unwanted_scores else 0

# # Логіка фільтрації
# if avg_unwanted > 0.90 and avg_desired < 0.70:
#     # Чіткі розваги (unwanted явно домінує)
#     keep_article = False
# elif avg_unwanted > 0.95 and (avg_unwanted - avg_desired) > 0.20:
#     # Екстремальне домінування unwanted (різниця >20%)
#     keep_article = False
# elif max_desired > 0.75 and avg_desired > 0.60 and avg_desired >= avg_unwanted * 0.85:
#     # Сильна серйозність + прийнятне середнє + unwanted не домінує сильно
#     keep_article = True
# elif avg_desired > 0.65 and avg_desired >= avg_unwanted * 0.95:
#     # Хороша серйозність + майже рівність
#     keep_article = True
# else:
#     # Сіра зона
#     keep_article = max_desired > 0.50 and avg_desired >= avg_unwanted * 0.90

# 4 варіант. Thresdhold
# Параметри
RELEVANCE_THRESHOLD = 0.70

# Отримуємо всі скори
desired_scores = sorted([score for label, score in zip(result["labels"], result["scores"]) 
                         if label in desired_labels], reverse=True)
unwanted_scores = sorted([score for label, score in zip(result["labels"], result["scores"]) 
                          if label in unwanted_labels], reverse=True)

# Максимуми (завжди є, якщо списки не порожні)
max_desired = desired_scores[0] if desired_scores else 0
max_unwanted = unwanted_scores[0] if unwanted_scores else 0

# Фільтруємо релевантні
relevant_desired = [s for s in desired_scores if s > RELEVANCE_THRESHOLD]
relevant_unwanted = [s for s in unwanted_scores if s > RELEVANCE_THRESHOLD]

# Середні та кількість
if relevant_desired:
    avg_desired = sum(relevant_desired) / len(relevant_desired)
    count_desired = len(relevant_desired)
else:
    # Fallback: якщо нічого не пройшло поріг, беремо топ-3
    avg_desired = sum(desired_scores[:3]) / min(len(desired_scores), 3) if desired_scores else 0
    count_desired = 0  # позначаємо, що це fallback

if relevant_unwanted:
    avg_unwanted = sum(relevant_unwanted) / len(relevant_unwanted)
    count_unwanted = len(relevant_unwanted)
else:
    # Fallback: якщо нічого не пройшло поріг, беремо топ-3
    avg_unwanted = sum(unwanted_scores[:3]) / min(len(unwanted_scores), 3) if unwanted_scores else 0
    count_unwanted = 0  # позначаємо, що це fallback

# Логіка фільтрації
if count_unwanted >= 3 and avg_unwanted > 0.90 and avg_desired < 0.75:
    # Багато високих unwanted
    keep_article = False
    print("✔️ 1 choice")
elif max_unwanted > 0.90 and max_unwanted > max_desired + 0.20:
    # ⚡ НОВА УМОВА: Явне домінування unwanted (різниця >20%)
    keep_article = False
    print("✔️ 2 choice")
elif count_unwanted > 0 and count_unwanted > count_desired and avg_unwanted > 0.95 and (avg_unwanted - avg_desired) > 0.15:
    # Екстремальне домінування unwanted
    keep_article = False
    print("✔️ 3 choice")
elif count_desired >= 2 and max_desired > 0.75 and avg_desired > 0.70 and (avg_unwanted < 0.90 or avg_desired >= avg_unwanted * 0.95):
    # Мінімум 2 сильні desired категорії
    keep_article = True
    print("✔️ 4 choice")
elif count_desired > 0 and avg_desired > 0.75 and avg_desired >= avg_unwanted * 0.90:
    # Високі desired + конкурентоспроможність
    keep_article = True
    print("✔️ 5 choice")
elif count_desired == 0 and count_unwanted == 0:
    # Обидва у fallback режимі
    keep_article = max_desired > 0.60 and avg_desired >= avg_unwanted
    # keep_article = avg_desired >= avg_unwanted
    print("✔️ 6 choice")
else:
    # Сіра зона
    keep_article = (max_desired > 0.60 and 
                   max_desired >= max_unwanted * 0.85 and
                   (avg_desired >= avg_unwanted * 0.85 or count_desired > count_unwanted))
    print("✔️ 7 choice")

print(f"Max:  desired={max_desired:.3f} | unwanted={max_unwanted:.3f}")
# print(f"Top-{TOP_N} avg: desired={avg_desired:.3f} | unwanted={avg_unwanted:.3f}")
print(f"Relevance-{RELEVANCE_THRESHOLD} avg: desired={avg_desired:.3f} | unwanted={avg_unwanted:.3f}")
print(f"Ratio: {avg_desired / (avg_unwanted + 0.01):.3f}")
# print(f"Top desired: {[f'{s:.2f}' for s in desired_scores]}")
# print(f"Top unwanted: {[f'{s:.2f}' for s in unwanted_scores]}")
print(f"Desired: {[f'{s:.2f}' for s in relevant_desired]}")
print(f"Unwanted: {[f'{s:.2f}' for s in relevant_unwanted]}")
print(f"{"✅" if keep_article else "❌"} Keep article is {keep_article}")

print('-'*50)
print(f"Classification took {toc-tic:.2f} seconds")
