#!/usr/bin/env python

# import spacy
from time import time
# import uk_core_news_sm
import uk_core_news_lg
# import ru_core_news_lg
# import uk_core_news_trf
# from spacy import displacy
from spacy.symbols import nsubj, VERB

# nlp = spacy.load("uk_core_news_lg")
# nlp = uk_core_news_sm.load()
nlp = uk_core_news_lg.load()
# nlp = uk_core_news_lg.load(disable=["parser"])
# nlp = ru_core_news_lg.load()
# nlp = uk_core_news_trf.load()


# If you do not want the tokenizer to split on hyphens between letters, you can modify the existing infix definition from lang/punctuation.py
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER
from spacy.lang.char_classes import CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.util import compile_infix_regex

# Modify tokenizer infix patterns
infixes = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[0-9])[+\\-\\*^](?=[0-9-])",
        r"(?<=[{al}{q}])\\.(?=[{au}{q}])".format(
            al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
        ),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        # ✅ Commented out regex that splits on hyphens between letters:
        # r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
        r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
    ]
)
infix_re = compile_infix_regex(infixes)
nlp.tokenizer.infix_finditer = infix_re.finditer


tic = time()
doc=nlp("Після удару РФ балістичними ракетами по місту Полтаві міністр закордонних справ України Дмитро Кулеба закликав партнерів прискорити доставку новітніх систем ППО і посилювати здатність України протидіяти балістичним атакам ворога.")
toc = time()
for token in doc:
    # print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop, token.morph)
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop, token.head.text, [child for child in token.children])
    if token.n_lefts or token.n_rights:
        print('⛓️‍', [t.text for t in token.lefts], token.text, [t.text for t in token.rights])
print("--------------------------------------------------")

# root = [token for token in doc if token.head == token][0]
# subject = list(root.lefts)[0]
# for descendant in subject.subtree:
#     assert subject is descendant or subject.is_ancestor(descendant)
#     print(descendant.text, descendant.dep_, descendant.n_lefts,
#             descendant.n_rights,
#             [ancestor.text for ancestor in descendant.ancestors])
# print("--------------------------------------------------")

for ent in doc.ents:
    print(ent.text, ent.lemma_, ent.start_char, ent.end_char, ent.label_)
print("--------------------------------------------------")

# The 'noun_chunks' syntax iterator is not implemented for language 'uk'.
# for chunk in doc.noun_chunks:
#     print(chunk.text, chunk.root.text, chunk.root.dep_, chunk.root.head.text)

# Finding a verb with a subject from below — good
# verbs = set()
# for possible_subject in doc:
#     if possible_subject.dep == nsubj and possible_subject.head.pos == VERB:
#         verbs.add(possible_subject.head)
# print(verbs)
# print("--------------------------------------------------")


# displacy.serve(doc, style="dep")
# displacy.serve(doc, style="ent", port=5001)

print(f"Elapsed {toc-tic:.3f} seconds")
