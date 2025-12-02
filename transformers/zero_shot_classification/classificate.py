#!/usr/bin/env python

from utils import classify_messages

# sequence_to_classify = "НАТО має намір збільшити кількість боєздатних бригад 131. Водночас заплановано вп'ятеро наростити кількість наземних підрозділів ППО."
sequence_to_classify = """
Только не "жаркоє" и "тушене м'ясо": как на украинском правильно назвать популярные блюда
"""

execution_time = classify_messages([sequence_to_classify], [sequence_to_classify])

print(f"⏱️ Classification took {execution_time:.2f} seconds")
