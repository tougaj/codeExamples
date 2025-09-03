#!/usr/bin/env python3

from time import time
from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification

# Завантажуємо модель і токенайзер
tokenizer = XLMRobertaTokenizer.from_pretrained("./model")
print("✅ Tokenizer loaded")
model = XLMRobertaForSequenceClassification.from_pretrained("./model")
print("✅ Model loaded")

tic = time()
# Класифікація нового тексту
test_text = """This movie was way over-hyped. A lot of the viewers, who thought this was ""amazing"" must have been into the old school movies, cause the whole movie is set in the past. At first I thought the movie was just showing something from the past, so I was expecting that faded dreamy like lighting on the characters to pass, but it just going. Basically this was a movie trying to mix the future with the past, and the 2 don't mix very well in this movie, even with special effects. You could actually see the blue screen the actors were working with. There are too many movies out there that do exactly what this movie did, so there is no reason for critics to hype this movie up saying ""it's the greatest movie ever done"". It's just crap on a stick. It also didn't help that the story line was sooo crappy. I don't understand why Hollywood agreed to have this movie produced, and I also don't understand how actors/actresses in this movie are willing to be in a movie like this. It's almost as though everybody read the script and forgot to read the fine print...""It will all be done on a computer"". This was a movie that should have been on a movie network, because nothing about this movie was revolutionary. I'm very upset with myself for paying money to see this. Whatever you do, don't waste your time and money on this movie today or tomorrow."""
inputs = tokenizer(test_text, return_tensors="pt", truncation=True, padding=True)
outputs = model(**inputs)

prediction = outputs.logits.argmax(dim=-1).item()
print("🤔 Прогноз:", prediction)  # 1 = підпадає під рубрику, 0 = ні
toc = time()
print(f"⏱️ Elapsed {toc-tic:.3f} seconds")

tic = time()
# Класифікація нового тексту
test_text = """It is incredible that there were two films with the same story released in 2005. This one came out a day before that other one with Tom Cruise. Didn't they do that with Truman Capote the same year, and the Zodiac killer last year? Interesting.<br /><br />Writer/Director David Michael Latt didn't have Steven Spielberg's budget and C. Thomas Howell is not Tom Cruise. This is a pale imitation of the blockbuster that grossed $588 million worldwide.<br /><br />The action was minimal and most of the time we were treated to the whining of Rhett Giles, who played a pastor that was giving up on his god.<br /><br />Gary Busey was creepy as an army LT."""
inputs = tokenizer(test_text, return_tensors="pt", truncation=True, padding=True)
outputs = model(**inputs)

prediction = outputs.logits.argmax(dim=-1).item()
print("🤔 Прогноз:", prediction)  # 1 = підпадає під рубрику, 0 = ні
toc = time()
print(f"⏱️ Elapsed {toc-tic:.3f} seconds")

tic = time()
# Класифікація нового тексту
test_text = """On watching this film, I was amazed at how media perception can mould a persons opinion of a celebrity. Karen Carpenter was a carefree, but very unconfident young lady, whose wonderful voice helped her and her brother Richard to soar the charts with wonderful songs. As with all celebrities of today, they were often criticised about their music as well as their looks, styles, etc. THis had a huge effect on Karen who raged a battle against her eating and drastically lost weight, which eventually caused her death. This heart felt film was not initially something which I would have thought of watching. But on starting to view it, then I was hooked. In the same way that the Tina Turner story does, then this film enlightens you and allows you to see into the young performers life. The acting was superb and even after nearly 20 years after it was made, then the directional and the dialogue are still entertaining.<br /><br />I would recommend this to anyone who hasn't yet watched it. It is amazingly accurate and emotionally charged."""
inputs = tokenizer(test_text, return_tensors="pt", truncation=True, padding=True)
outputs = model(**inputs)

prediction = outputs.logits.argmax(dim=-1).item()
print("🤔 Прогноз:", prediction)  # 1 = підпадає під рубрику, 0 = ні
toc = time()
print(f"⏱️ Elapsed {toc-tic:.3f} seconds")
