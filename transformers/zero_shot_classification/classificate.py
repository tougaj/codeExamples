#!/usr/bin/env python

from transformers import pipeline
from time import time
import sys
from pprint import pprint

# Multiplier (Рішення 3): простіший, фіксовані коефіцієнти (1.05, 1.08, 1.10)
def calculate_metrics(relevant_scores, all_scores):
    """
    Обчислює avg та count з урахуванням бонусу за кількість категорій.
    
    Args:
        relevant_scores: список скорів вище threshold
        all_scores: всі скори (для fallback)
    
    Returns:
        tuple: (avg, count)
    """
    if relevant_scores:
        max_score = relevant_scores[0]
        count = len(relevant_scores)
        
        # Комбінований score: max + бонус за кількість
        if count >= 5:
            avg = min(max_score * 1.10, 1.0)
        elif count >= 4:
            avg = min(max_score * 1.08, 1.0)
        elif count >= 3:
            avg = min(max_score * 1.05, 1.0)
        else:
            avg = max_score
    else:
        # Fallback: якщо нічого не пройшло поріг, беремо топ-3
        avg = sum(all_scores[:3]) / min(len(all_scores), 3) if all_scores else 0
        count = 0  # позначаємо, що це fallback
    
    return avg, count

# Bonus (Рішення 2): гнучкіший, враховує значення кожної категорії, а не тільки кількість
def calculate_metrics_with_bonus(relevant_scores, all_scores):
    """
    Обчислює avg та count з урахуванням бонусу за додаткові категорії.
    
    Базовий score = max, але кожна додаткова релевантна категорія дає бонус.
    
    Args:
        relevant_scores: список скорів вище threshold
        all_scores: всі скори (для fallback)
    
    Returns:
        tuple: (avg, count)
    """
    if relevant_scores:
        base_score = relevant_scores[0]  # максимальний
        count = len(relevant_scores)
        
        # Бонус за кожну додаткову релевантну категорію (зменшується)
        bonus = 0
        for i, score in enumerate(relevant_scores[1:], start=1):
            # Кожна наступна дає менший бонус: 3%, 2%, 1.5%, 1%, 0.75%...
            bonus += score * (0.03 / i)
        
        avg = min(base_score + bonus, 1.0)  # не більше 1.0
    else:
        # Fallback: якщо нічого не пройшло поріг, беремо топ-3
        avg = sum(all_scores[:3]) / min(len(all_scores), 3) if all_scores else 0
        count = 0  # позначаємо, що це fallback
    
    return avg, count

def calculate_metrics_combined(relevant_scores, all_scores):
    """
    Обчислює метрики з комбінованим підходом.
    
    Повертає combined score як avg (для сумісності) та додаткові метрики.
    
    Args:
        relevant_scores: список скорів вище threshold
        all_scores: всі скори (для fallback)
    
    Returns:
        tuple: (avg, count, max_score, true_avg)
            - avg: комбінований скор (використовується як основний)
            - count: кількість релевантних категорій (0 якщо fallback)
            - max_score: максимальний скор (для додаткових перевірок)
            - true_avg: справжнє середнє арифметичне (для додаткових перевірок)
    """
    if relevant_scores:
        max_score = relevant_scores[0]
        count = len(relevant_scores)
        true_avg = sum(relevant_scores) / len(relevant_scores)
        
        # Комбінований score: max + бонус за кількість
        if count >= 5:
            combined_score = max_score * 1.10
        elif count >= 4:
            combined_score = max_score * 1.08
        elif count >= 3:
            combined_score = max_score * 1.05
        else:
            combined_score = max_score
        
        # Обмежуємо максимум 1.0
        avg = min(combined_score, 1.0)
        
    else:
        # Fallback: якщо нічого не пройшло поріг, беремо топ-3
        if all_scores:
            top_3 = all_scores[:3]
            avg = sum(top_3) / len(top_3)
            max_score = all_scores[0]
            true_avg = avg
        else:
            avg = 0
            max_score = 0
            true_avg = 0
        
        count = 0  # позначаємо fallback
    
    return avg, count, max_score, true_avg

model = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
classifier = pipeline("zero-shot-classification", model=model, tokenizer=model)
# classifier = pipeline("zero-shot-classification", model="vicgalle/xlm-roberta-large-xnli-anli")
# classifier = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")

# sequence_to_classify = "НАТО має намір збільшити кількість боєздатних бригад 131. Водночас заплановано вп'ятеро наростити кількість наземних підрозділів ППО."
sequence_to_classify = """
Зеленский с супругой прибыли в Дублин: их встретил премьер Ирландии. Видео
Президент Украины Владимир Зеленский во вторник, 2 декабря, прибыл с первым визитом в Ирландию. Вместе с ним в Дублин прибыла и первая леди Елена Зеленская.
Об этом сообщает ирландский телеканал RTE. Глава государства и первая леди проведут ряд правительственных встреч.Визит Зеленских в Ирландию
Согласно данным мониторингового авиаресурса AirNav, президентский самолет Airbus A319 UR-ABA государственной украинской авиакомпании Ukraine Air Enterprise в 22:47 по ирландскому времени (00:47 по киевск
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
# if relevant_desired:
#     avg_desired = sum(relevant_desired) / len(relevant_desired)
#     count_desired = len(relevant_desired)
# else:
#     # Fallback: якщо нічого не пройшло поріг, беремо топ-3
#     avg_desired = sum(desired_scores[:3]) / min(len(desired_scores), 3) if desired_scores else 0
#     count_desired = 0  # позначаємо, що це fallback

# if relevant_unwanted:
#     avg_unwanted = sum(relevant_unwanted) / len(relevant_unwanted)
#     count_unwanted = len(relevant_unwanted)
# else:
#     # Fallback: якщо нічого не пройшло поріг, беремо топ-3
#     avg_unwanted = sum(unwanted_scores[:3]) / min(len(unwanted_scores), 3) if unwanted_scores else 0
#     count_unwanted = 0  # позначаємо, що це fallback

avg_desired, count_desired = calculate_metrics_with_bonus(relevant_desired, desired_scores)
avg_unwanted, count_unwanted = calculate_metrics_with_bonus(relevant_unwanted, unwanted_scores)

# avg_desired, count_desired = calculate_metrics(relevant_desired, desired_scores)
# avg_unwanted, count_unwanted = calculate_metrics(relevant_unwanted, unwanted_scores)

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
    # keep_article = max_desired > 0.60 and avg_desired >= avg_unwanted
    keep_article = max_desired > 0.50 and avg_desired >= avg_unwanted
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
