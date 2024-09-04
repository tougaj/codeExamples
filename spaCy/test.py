#!/usr/bin/env python

# import spacy
from time import time
# import uk_core_news_sm
import uk_core_news_lg
# import ru_core_news_lg
# import uk_core_news_trf

# nlp = uk_core_news_sm.load()
nlp = uk_core_news_lg.load()
# nlp = ru_core_news_lg.load()
# nlp = uk_core_news_trf.load()
tic = time()
doc=nlp("Після удару РФ балістичними ракетами по місту Полтава міністр закордонних справ України Дмитро Кулеба закликав партнерів прискорити доставку новітніх систем ППО і посилювати здатність України протидіяти балістичним атакам ворога.")
toc = time()
for token in doc:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop)
print("--------------------------------------------------")
for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)
print("--------------------------------------------------")
print(f"Elapsed {toc-tic:.3f} seconds")
