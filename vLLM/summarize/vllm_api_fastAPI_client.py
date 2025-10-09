"""
🌐 Клієнт для роботи з vLLM OpenAI-compatible API
Використовує офіційну openai бібліотеку для summarization
"""

import time
from dataclasses import dataclass
from pprint import pprint
from typing import Dict, List, Optional

import requests

from common import news_headlines, texts

PORT = 8000
SERVER_ADDRESS = f"http://localhost:{PORT}"


@dataclass
class SummarizationConfig:
    """Конфігурація для різних типів summarization"""
    temperature: float
    top_p: float
    max_tokens: int
    presence_penalty: float
    frequency_penalty: float
    stop: Optional[List[str]] = None


# 🎯 Готові конфігурації
# CONFIGS = {
#     "precise": SummarizationConfig(
#         temperature=0.2,
#         top_p=0.85,
#         max_tokens=200,
#         presence_penalty=0.6,
#         frequency_penalty=0.4,
#         # stop=["</summary>", "\n\n\n", "Текст:"]
#     ),
#     "balanced": SummarizationConfig(
#         temperature=0.5,
#         top_p=0.9,
#         max_tokens=4196,
#         presence_penalty=0.5,
#         frequency_penalty=0.3,
#         # stop=["</summary>", "\n\n\n"]
#     ),
#     "creative": SummarizationConfig(
#         temperature=0.8,
#         top_p=0.95,
#         max_tokens=600,
#         presence_penalty=0.3,
#         frequency_penalty=0.2,
#         # stop=["</summary>", "\n\n\n"]
#     ),
# }


def check_health() -> bool:
    """
    Перевірка доступності сервера
    """
    try:
        response = requests.get(f"{SERVER_ADDRESS}/health")
        print(f"✅ Сервер доступний. Параметри:")
        pprint(response.json())
        return True
    except Exception as e:
        print(f"❌ Сервер недоступний: {e}")
        return False


def print_results(texts: list[str], results: requests.Response, route: str):
    if results.status_code == 200:
        data = results.json()
        for i, (result, text) in enumerate(zip(data['results'], texts), 1):
            print(f"📄 Текст #{i}: {text[:50]}")
            print(f"✨ {route}: {result['text']}")
            print(f"✳️ Причина зупинки: {result['finish_reason']}\n")
    else:
        print(f"Помилка: {results.status_code}, {results.text}")


def process(texts: list[str], route: str):
    print(f"{route}\n{'-'*30}")
    start_time = time.time()
    results = requests.post(f"{SERVER_ADDRESS}/{route}", json={
        "texts": texts,
        # "sampling_params": {
        #     "temperature": 0.7,
        #     "top_p": 0.9,
        #     "max_tokens": 8192
        # }
    })
    end_time = time.time()
    print_results(texts, results, route)
    print(f"⏱️ Відповідь зайняла {end_time - start_time:.4f} секунд\n")


# 📊 Приклади використання
if __name__ == "__main__":
    # 🏥 Перевірка здоров'я сервера
    print("="*30)
    print("🏥 Перевірка підключення до сервера")
    print("="*30 + "\n")

    if not check_health():
        print("\n⚠️  Переконайся, що vLLM сервер запущений!")
        print("Запусти: uv run fastAPI/main.py")
        exit(1)

    # Batch-обробка
    print("="*30)
    print("📦 Тест batch-обробки")
    print("="*30 + "\n")

    # batch_texts = news_headlines
    batch_texts = texts

    iteration_count = 1
    for i in range(iteration_count):
        print(f"🫧 Iteration {i+1}/{iteration_count}\n{'*'*30}")
        process(batch_texts, 'translate')
        process(batch_texts, 'summarize')
