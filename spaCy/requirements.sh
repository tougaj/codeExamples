#!/usr/bin/env bash

# python -m venv .env
source venv/bin/activate
pip install -U pip setuptools wheel
pip install -U spacy
# pip install -U jupyter
# python -m spacy download uk_core_news_sm
python -m spacy download uk_core_news_lg
# python -m spacy download uk_core_news_trf
