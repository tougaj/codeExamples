#!/usr/bin/env python

import spacy
# import uk_core_news_lg

# from spacy.lang.uk import Ukrainian

nlp = spacy.load("uk_core_news_lg")
# nlp = spacy.load("en_core_web_lg")
# nlp = spacy.load("ru_core_news_lg")

# nlp = uk_core_news_lg.load()

# ruler = nlp.add_pipe("entity_ruler", before="ner")
ruler = nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})
patterns = [
    {
        "label": "LOC",
        "pattern": [
            {"ENT_TYPE": "LOC"},
            {"TEXT": "-"},
            {"ENT_TYPE": "LOC"},
        ]
    },
    {
        "label": "ORG",
        "pattern": [
            {"ENT_TYPE": "ORG"},
            {"TEXT": "-"},
            {"ENT_TYPE": "ORG"},
        ]
    },
    {
        "label": "PER",
        "pattern": [
            {"ENT_TYPE": "PER", "OP": "?"},
            {"ENT_TYPE": "PER"},
            {"TEXT": "-"},
            {"ENT_TYPE": "PER"}
        ]
    },
]
ruler.add_patterns(patterns)
doc = nlp("""Група таких-собі комунальників з Івано-Франківська вирушила на Донеччину для будівництва оборонних споруд. Про співробітників підприємства Водоканал-Сервіс розпитаємо в наших кореспондентів Жанни Дутчак-Малиновської та Степана Боброва.""")
# docs = nlp.pipe(['Група таких-собі комунальників з Івано-Франківська вирушила на Донеччину для будівництва оборонних споруд. Про співробітників підприємства Водоканал-Сервіс розпитаємо в наших кореспондентів Жанни Дутчак-Малиновської та Степана Боброва.'], n_process=2)
# doc = list(docs)[0]

for token in doc:
    print('🔷', token.text, token.lemma_, token.pos_, token.dep_, token.shape_, token.is_stop,
          f'ent_type={token.ent_type_}' if token.ent_type_ else '', token.is_upper, token.is_title)
print("-------------------------")

for ent in doc.ents:
    print('🔶', ent.text, ent.lemma_, ent.start_char, ent.end_char, ent.label_)
print("-------------------------")

unique_ents = set()
for ent in doc.ents:
    unique_ents.add(ent.lemma_)
for e in unique_ents:
    print(e)
print("-------------------------")


# merged_entities = []
# current_entity = None

# for ent in doc.ents:
#     if current_entity is None:
#         current_entity = ent
#     else:
#         # Перевірка на однаковий label і чи можна об'єднати (різниця 0 або 1)
#         if current_entity.label_ == ent.label_ and (ent.start_char - current_entity.end_char) <= 1:
#             # Оновлюємо текст, end_char для об'єднаної сутності
#             current_entity = spacy.tokens.Span(
#                 doc, current_entity.start, ent.end, label=current_entity.label_)
#         else:
#             # Додаємо поточну сутність у список
#             merged_entities.append(current_entity)
#             current_entity = ent

# # Не забудьте додати останню сутність після циклу
# if current_entity:
#     merged_entities.append(current_entity)

# # Виводимо результат
# for ent in merged_entities:
#     print('🔶', ent.text, ent.lemma_, ent.start_char, ent.end_char, ent.label_)


# Можна так:import spacy
# from spacy.tokens import Span

# # Функція для об'єднання сутностей
# def merge_entities(doc):
#     merged_ents = []
#     current_ent = None

#     for ent in doc.ents:
#         if current_ent is None:
#             current_ent = ent
#         else:
#             if current_ent.label_ == ent.label_ and (ent.start_char - current_ent.end_char) <= 1:
#                 # Оновлюємо сутність
#                 current_ent = Span(doc, current_ent.start, ent.end, label=current_ent.label_)
#             else:
#                 # Додаємо попередню сутність
#                 merged_ents.append(current_ent)
#                 current_ent = ent

#     # Додаємо останню сутність
#     if current_ent:
#         merged_ents.append(current_ent)

#     # Оновлюємо сутності в документі
#     doc.ents = merged_ents
#     return doc

# # Завантажуємо модель SpaCy
# nlp = spacy.load("en_core_web_sm")

# # Додаємо компонент у pipeline
# nlp.add_pipe(merge_entities, after="ner")

# # Тестування
# doc = nlp("Barack Obama was the 44th President of the United States.")
# for ent in doc.ents:
#     print(ent.text, ent.lemma_, ent.start_char, ent.end_char, ent.label_)
