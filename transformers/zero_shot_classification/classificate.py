#!/usr/bin/env python

from pprint import pprint
from time import time

from utils import classify_messages

# sequence_to_classify = "НАТО має намір збільшити кількість боєздатних бригад 131. Водночас заплановано вп'ятеро наростити кількість наземних підрозділів ППО."
sequence_to_classify = """
Всегда был на своем месте: на фронте погиб звукорежиссер Эдуард Павлов
В боях против российской оккупационной армии погиб военнослужащий Эдуард Павлов. Жизнь защитника <b>оборвалась на 53 году.</b>
Видео дня
До войны Эдуард <b>более 20 лет работал в сфере звука. </b>Об этом в Facebook сообщает общественная организация PEN Ukraine.Отдал жизнь за Украину
В течение многих лет мужчина в сети пабов Docker. Он был <b>известен как мастер своего дела</b>, обеспечивающий качественный звук на концертах и ​​мероприятиях.
"Концерты, репетиции, тысячи моментов, где он творил
"""

# tic = time()
# sequences = [sequence_to_classify] * 10
# results = classifier(sequences, all_labels, multi_label=True)
# toc = time()
# pprint(results)
# print('-'*50)
# print(f"Classification took {toc-tic:.2f} seconds")
# sys.exit()

tic = time()
result = classify_messages([sequence_to_classify], [sequence_to_classify])
toc = time()

print('-'*50)
print(f"Classification took {toc-tic:.2f} seconds")
