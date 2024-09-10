#!/usr/bin/env python

# import spacy
from time import time

# import uk_core_news_sm
import uk_core_news_lg
# import ru_core_news_lg
# import uk_core_news_trf
# from spacy import displacy
from spacy.lang.char_classes import (ALPHA, ALPHA_LOWER, ALPHA_UPPER,
                                     CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS)
# from spacy.symbols import VERB, nsubj
from spacy.util import compile_infix_regex


def get_source_text():
    content = ''
    with open('local.text.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def adjust_tokenizer(nlp):
    # If you do not want the tokenizer to split on hyphens between letters, you can modify the existing infix definition from lang/punctuation.py
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
    # For an overview of the default regular expressions, see lang/punctuation.py and language-specific definitions such as https://github.com/explosion/spaCy/blob/master/spacy/lang/en/punctuation.py


def print_sentences(doc):
    for sent in doc.sents:
        print(sent.text)
    print("--------------------------------------------------")


def print_tokens(doc, with_lr=True):
    for token in doc:
        # print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop, token.morph)
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_,
              token.is_alpha, token.is_stop, token.head.text, [child for child in token.children])
        if with_lr and (token.n_lefts or token.n_rights):
            print('⛓️‍', [t.text for t in token.lefts], '<-',
                  token.text, '->', [t.text for t in token.rights])
    print("--------------------------------------------------")


def print_entities(doc):
    for ent in doc.ents:
        print(ent.text, ent.lemma_, ent.start_char, ent.end_char, ent.label_)
    print("--------------------------------------------------")


# nlp = spacy.load("uk_core_news_lg")
# nlp = uk_core_news_sm.load()
nlp = uk_core_news_lg.load()
# nlp = uk_core_news_lg.load(disable=["parser"])
# nlp = ru_core_news_lg.load()
# nlp = uk_core_news_trf.load()

# adjust_tokenizer(nlp)

tic = time()
doc = nlp(get_source_text())
toc = time()

print_sentences(doc)
print_tokens(doc, True)
print_entities(doc)


# root = [token for token in doc if token.head == token][0]
# subject = list(root.lefts)[0]
# for descendant in subject.subtree:
#     assert subject is descendant or subject.is_ancestor(descendant)
#     print(descendant.text, descendant.dep_, descendant.n_lefts,
#           descendant.n_rights,
#           [ancestor.text for ancestor in descendant.ancestors])
# print("--------------------------------------------------")


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
