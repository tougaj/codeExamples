import spacy

# from spacy.lang.uk import Ukrainian

nlp = spacy.load("uk_core_news_lg")
ruler = nlp.add_pipe("entity_ruler", before="ner")
# ruler = nlp.add_pipe("entity_ruler")
patterns = [
    {
        "label": "RRR",
        "pattern": [
            {"LEMMA": "івано"},
            {"TEXT": "-"},
            {"LEMMA": "франківськ"},

            # {"ENT_TYPE": "LOC"},
            # {"DEP": "amod"},
            # {"DEP": "nmod"},
            # {"ENT_TYPE": "LOC"},
            # {"LEMMA": "вирушити"}

            # {"POS": "PROPN", "OP": "?"},
            # {"POS": "PROPN"},
            # {"TEXT": "-"},
            # {"POS": "PROPN"}
        ]
        # "label": "RRR",
        # "pattern": [
        #     {"LEMMA": "оборонний"},
        #     {"LEMMA": "споруда"}
        # ]
    },
    {
        "label": "PER",
        "pattern": [
            {"DEP": "flat:title", "OP": "?"},
            {"DEP": "flat:name"},
            {"TEXT": "-"},
            {"DEP": "flat:name"}
        ]
    },
]
# patterns = [{"label": "LOC", "pattern": [
#     {"LEMMA": "оборонний"}, {"LEMMA": "споруда"}]}]
# ruler.add_patterns(patterns)
# [{"label": "ORG", "pattern": "Apple"}]
#             {"label": "GPE", "pattern": [{"LOWER": "san"}, {"LOWER": "francisco"}]}]
ruler.add_patterns(patterns)
doc = nlp('Група таких-собі комунальників з Івано-Франківська вирушила на Донеччину для будівництва оборонних споруд. Співробітників підприємства Водоканал-Сервіс розпитають наши кореспонденти Жанна Дутчак-Малиновська та Степан Бобров.')

for token in doc:
    print('🔷', token.text, token.lemma_, token.pos_, token.dep_, token.shape_, token.is_stop,
          f'ent_type={token.ent_type_}' if token.ent_type_ else '', token.is_upper, token.is_title)
print("--------------------------------------------------")

for ent in doc.ents:
    print(ent.text, ent.lemma_, ent.start_char, ent.end_char, ent.label_)
print("--------------------------------------------------")
