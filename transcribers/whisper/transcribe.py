#!/usr/bin/env python3

import os
import sys
from datetime import timedelta
from time import time

import whisper


def format_timestamp(seconds: float) -> str:
    """Форматує час у вигляді MM:SS.mmm"""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    milliseconds = int((seconds - total_seconds) * 1000)
    minutes, secs = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    # Ми використовуємо лише хвилини та секунди, бо приклад не має годин
    return f"{minutes:02d}:{secs:02d}.{milliseconds:03d}"


def main():
    if len(sys.argv) != 2:
        print("Використання: python3 transcribe.py <шлях_до_аудіофайлу>")
        sys.exit(1)

    audio_path = sys.argv[1]
    if not os.path.isfile(audio_path):
        print(f"Помилка: файл '{audio_path}' не знайдено.")
        sys.exit(1)

    # Створюємо каталог results, якщо його немає
    os.makedirs("results", exist_ok=True)

    # Генеруємо ім'я вихідного файлу
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_path = os.path.join("results", f"{base_name}.txt")

    print(f"Завантаження моделі Whisper 'turbo'...")
    model = whisper.load_model("turbo")

    print(f"Транскрибація файлу: {audio_path}")
    tic = time()
    result = model.transcribe(
        audio_path,
        language=None,
        task="transcribe",
        verbose=True
    )
    toc = time()

    # Записуємо результат у форматі субтитрів
    with open(output_path, "w", encoding="utf-8") as f:
        for segment in result["segments"]:
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()
            f.write(f"[{start} --> {end}]  {text}\n")

    print(f"✅ Транскрибацію збережено у: {output_path}")
    print(f"⏱️ Час виконання: {str(timedelta(seconds=round(toc - tic)))}")


if __name__ == "__main__":
    main()
