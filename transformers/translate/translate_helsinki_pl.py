#!/usr/bin/env python

from transformers import pipeline
import nltk
# nltk.download('punkt')  # Завантажуємо необхідні дані для токенізації
from nltk.tokenize import sent_tokenize
from time import time

translator = pipeline("translation", model="Helsinki-NLP/opus-mt-pl-uk")

text = """Nie można zakazać producentom roślinnych alternatyw dla mięsa używania nazw typu „stek roślinny”, „szynka sojowa”, „boczek wegetariański” lub „kiełbasa warzywna” – wynika z piątkowego wyroku TSUE rozstrzygającego spór między francuską grupą lobbingową Protéines France a państwem francuskim, które poprzez taki zakaz zamierzało wzmocnić sektor hodowców zwierząt i producentów wyrobów z mięsa.
Cztery podmioty działające w sektorze produktów wegetariańskich i wegańskich (Stowarzyszenie Protéines France, Union végétarienne européenne, Association végétarienne de France i spółka Beyond Meat Inc.) zakwestionowały dekret, który francuskiego rządu zakazujący stosowania takich nazw jak „kotlet”, "burger", "stek" lub "szynka" i „kiełbasa” z dodatkowym przymiotnikiem „roślinny”, "warzywny" lub „sojowy”, a także bez niego, do oznakowania produktów białkowych pochodzenia roślinnego. Według grupy podmiotów, zakaz narusza unijne rozporządzenie nr 1169/2011 w sprawie przekazywania konsumentom.
W piątkowym wyroku Trybunał wskazał, że prawo Unii ustanawia wzruszalne domniemanie, zgodnie z którym informacje przekazywane zgodnie z zasadami określonymi w rozporządzeniu nr 1169/2011 chronią w wystarczającym stopniu konsumentów, w tym w przypadku całkowitego zastąpienia jedynego komponentu lub składnika, którego znalezienia konsumenci mogą się spodziewać w środku spożywczym oznaczonym nazwą zwyczajową lub nazwą opisową zawierającą pewne terminy.
- Państwo członkowskie nie może za pomocą ogólnego i abstrakcyjnego zakazu zabronić producentom środków spożywczych na bazie białek roślinnych używania nazw zwyczajowych lub nazw opisowych – podkreślił TSUE w wyroku.
TSUE podkreślił, że państwo może zakazać używania „nazw zwyczajowych” do oznaczenia produktu spożywczego, jeśli takie oznaczenie przyjmie konkretną nazwę prawną dla określonego środka spożywczego.
- Zakaz stosowania pewnych terminów do oznaczania żywności o pewnych właściwościach (skład itp.) nie jest równoznaczny z przyjętymi przez państwo wymogami, które musi spełniać produkt, aby można było oznaczyć go za pomocą nazw przewidzianych w przepisach. Jedynie takie przepisy mogą zapewnić ochronę konsumenta, który chce mieć gwarancję, że środek spożywczy oznaczony nazwą przewidzianą w przepisach, spełnia warunki przewidziane specjalnie dla tej tej nazwy – wyjaśnił Trybunał.
Jednocześnie sędziowie TSUE zaznaczyli, że państwa członkowskie zawsze mogą interweniować, jeśli „konkretne ustalenia dotyczące metod sprzedaży lub promocji żywności wprowadzają konsumenta w błąd”.
Konkluzja: państwo członkowskie może zdefiniować w swoich przepisach co jest kiełbasą lub stekiem. W przeciwnym wypadku nie może zakazać producentom wegańskich wyrobów wywiązania się z obowiązku wskazania nazwy produktu roślinnego poprzez użycie nazwy „kiełbasa”, „stek” itp.
Wyrok TSUE będzie miał bezpośredni wpływ na oznakowanie produktów wyprodukowanych we Francji, ale ma znaczenie także dla pozostałych państw członkowskich, które chciałby wdrożyć rozwiązania podobne do francuskich."""
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