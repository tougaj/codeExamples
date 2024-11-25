#!/usr/bin/env python3

import whisper
import json
# import pprint

model = whisper.load_model("turbo")
result = model.transcribe(
    "test.mp4",
    language=None,       # Автоматичне визначення мов
    task="transcribe",   # Завдання: транскрипція
    verbose=True         # Виведення прогресу
)

# Збереження в файл JSON
with open("result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

print("Результат записано у файл result.json")
# pprint.pp(result)
# print(result["text"])

for segment in result["segments"]:
    print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s]: ({segment.get('language')}) {segment['text']}")
