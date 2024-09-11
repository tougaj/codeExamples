import spacy

# from spacy.lang.uk import Ukrainian

nlp = spacy.load("uk_core_news_lg")
# ruler = nlp.add_pipe("entity_ruler", before="ner")
ruler = nlp.add_pipe("entity_ruler", validate=True)
# ruler = nlp.add_pipe("entity_ruler", before="ner")
patterns = [
    {
        "label": "RRR",
        "pattern": [
            # {"ENT_TYPE": "LOC"},
            # {"LEMMA": "івано"},
            {"POS": "PROPN"},
            {"TEXT": "-"},
            {"POS": "PROPN"},
            # {"ENT_TYPE": "LOC"},
            # {"LEMMA": "франківськ"}
        ]
    }
]
# patterns = [{"label": "LOC", "pattern": [
#     {"LEMMA": "оборонний"}, {"LEMMA": "споруда"}]}]
# ruler.add_patterns(patterns)
# [{"label": "ORG", "pattern": "Apple"}]
#             {"label": "GPE", "pattern": [{"LOWER": "san"}, {"LOWER": "francisco"}]}]
ruler.add_patterns(patterns)
doc = nlp('Група таких-собі комунальників з Івано-Франківська вирушила на Донеччину для будівництва оборонних споруд. Співробітників підприємства Водоканал-Сервіс розпитала наша кореспондентка Жанна Дутчак-Малиновська.')

for token in doc:
    print('🔷', token.text, token.lemma_, token.pos_, token.dep_, token.shape_, token.is_stop,
          f'ent_type={token.ent_type_}' if token.ent_type_ else '', token.is_upper, token.is_title)
print("--------------------------------------------------")

for ent in doc.ents:
    print(ent.text, ent.lemma_, ent.start_char, ent.end_char, ent.label_)
print("--------------------------------------------------")
