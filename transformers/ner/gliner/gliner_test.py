#!/usr/bin/env python

import stanza
from gliner import GLiNER

# Завантаження української моделі один раз
stanza.download("uk")
nlp = stanza.Pipeline("uk", processors="tokenize,mwt,pos,lemma", use_gpu=False)

model = GLiNER.from_pretrained("urchade/gliner_multi-v2.1")

text = """
Ціни на нафту у середу, 11 червня, знизилися на азійських торгах, оскільки ринок оцінював результати торговельних перемовин між США й Китаєм. Водночас слабкий попит на нафту з боку Китаю та зростання видобутку ОПЕК+ вплинули на котирування.
Як передає Укрінформ, про це повідомляє enkorr з посиланням на Reuters.
Ф’ючерси на нафту Brent знизилися на 19 центів (0,3%) — до $66,68 за барель, а West Texas Intermediate (WTI) здешевшала на 16 центів (0,3%) — до $64,82 за барель.
Міністр торгівлі США Говард Лутнік заявив у вівторок, що після двох днів інтенсивних перемовин у Лондоні офіційні представники США й Китаю домовилися про рамкову угоду щодо повернення до торговельного перемир’я і врегулювання експортних обмежень Китаю на рідкісноземельні мінерали й магніти.
Ринковий аналітик Філіп Нова зазначив, що поточні цінові корекції можна пояснити поєднанням технічної фіксації прибутку й обережності перед офіційними заявами США й Китаю.
Президент Дональд Трамп ще не розглянув результати перемовин, але очікується, що вони можуть підтримати попит на нафту, стабілізувавши економічні перспективи США й Китаю.
Альянс ОПЕК+ планує збільшити видобуток нафти на 411 тис. барелів на добу (б/д) у липні, прагнучи скасувати скорочення виробництва четвертий місяць поспіль.
Аналітики Capital Economics зазначають, що зростання попиту в країнах ОПЕК+, зокрема в Саудівській Аравії, може компенсувати додаткове постачання й підтримати ціни на нафту у найближчі місяці.
Однак економіст Хамад Хуссейн підкреслює, що підвищення попиту буде сезонним, тому Capital Economics очікує, що ціни на Brent можуть знизитися до $60 за барель до кінця року.
У середу ринок також зосередиться на щотижневому звіті про запаси нафти в США від Управління енергетичної інформації.
За даними Американського інституту нафти, запаси сирої нафти у США минулого тижня впали на 370 тис. б/д.
Аналітики Reuters прогнозували, що запаси сирої нафти в США скоротяться на 2 млн барелів за тиждень до 6 червня, тоді як запаси дистилятів і бензину можуть зрости.
"""

labels = ["person", "organization", "location", "country", "city", "region", "date", "time", "money", "percent", "event", "law", "product", "work_of_art", "language", "ethnic_group", "profession", "disease", "technology", "quantity"]

entities = model.predict_entities(text, labels)

def lemmatize_uk(text):
    doc = nlp(text)
    lemmas = [word.lemma for sent in doc.sentences for word in sent.words]
    return " ".join(lemmas)

seen = set()
unique_entities = []

for entity in entities:
    text = entity["text"].strip().lower()
    lemma = lemmatize_uk(text)
    key = (lemma, entity["label"])
    if key not in seen:
        seen.add(key)
        unique_entities.append({
            "text": entity["text"],  # залишаємо оригінальний текст
            "label": entity["label"],
            "lemma": lemma
        })

# Опціональний вивід
for item in unique_entities:
    print(f"{item['text']} => {item['label']} | Лема: {item['lemma']}")

# for entity in entities:
#     lemmatized = lemmatize_uk(entity["text"])
#     print(f"{entity['text']} => {entity['label']} | Лема: {lemmatized}")
