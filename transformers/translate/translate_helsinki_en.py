#!/usr/bin/env python

from transformers import pipeline
import nltk
nltk.download('punkt_tab')  # Завантажуємо необхідні дані для токенізації
from nltk.tokenize import sent_tokenize
from time import time

translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-uk")

text = """The essence of a thriving economy is grounded in adherence to free-market principles and a level playing field for all. The proposed $14.9 billion acquisition of U.S. Steel by Japan-based Nippon Steel presents a test case for the free market. Unfortunately, it is mired in a political controversy that threatens to overshadow its prospective economic benefits.
At the heart of the matter is a clear divergence from standard procedural integrity. Recent developments reveal an unsettling trend toward the politicization of the Committee on Foreign Investment in the United States. This trend has been spearheaded by President Joe Biden’s premature critique of the deal. His comments, suggesting a preference for maintaining U.S. Steel as an “American steel company,” have sparked concerns among free-market conservatives. They argue that such political interference could derail a thorough, unbiased review by CFIUS, whose mandate is to evaluate the implications of such foreign investments purely on national security grounds.
This intervention is not just a procedural misstep — it is a possible affront to the principles of free enterprise. The deal, proposed in December 2023, is under scrutiny not just for its economic implications but as a litmus test for America’s adherence to fair play in international commerce. Proponents of the acquisition, including key conservative leaders, argue convincingly that allowing Nippon Steel to take over could bolster the American workforce and enhance the U.S.-Japan alliance, better positioning both nations against economic pressures from China.
Moreover, the opposition, notably from the United Steelworkers union, stems from concerns over job security under foreign management. While these apprehensions are not without merit, they must be addressed within the framework of economic reality and fairness. The rival bid from Cleveland-Cliffs, though a domestic option, does not automatically translate to better prospects for American workers or the industry at large.
It is imperative that CFIUS operates devoid of political influence, focusing solely on the national security implications of the proposed deal. The Biden administration’s overt signals, however, complicate this objective, potentially prejudicing the review process. Such maneuvers not only undermine the credibility of CFIUS but also signal to international investors that U.S. economic policies may be swayed by political currents, rather than being anchored in law and economic rationale.
The situation calls for a return to principles. The administration must reaffirm its commitment to a fair review process by CFIUS. This is crucial not only for the integrity of U.S. economic policy frameworks but also for maintaining the trust of international partners and investors. As global competition intensifies, especially with China, the U.S. cannot afford to be seen as a country where political expediency trumps economic logic and security considerations.
The Nippon Steel acquisition of U.S. Steel should be evaluated on its merits, through an unobstructed and apolitical lens.
This is not just about one company or one industry — it is about maintaining the foundational pillars of our economic system, ensuring that America remains a beacon of free enterprise and fair play on the global stage.
Amanda Peterson is an economic and political analyst and activist based in America’s steel manufacturing heartland. She is president of Excelsior Podcast Studios in Minneapolis and writes extensively on economic policy that impacts the Great Lakes Region."""
sentences = sent_tokenize(text)

tic = time()
result = translator(sentences)
toc = time()
elapsed = toc-tic
print('-'*50)
for r in result:
	print(r['translation_text'])
print('-'*50)
print(f"{len(sentences)} sentences have been translated {toc-tic:.2f} seconds ({(toc-tic)/len(sentences):.2f} sec/sentence)")