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
CONFIGS = {
    "precise": SummarizationConfig(
        temperature=0.2,
        top_p=0.85,
        max_tokens=200,
        presence_penalty=0.6,
        frequency_penalty=0.4,
        # stop=["</summary>", "\n\n\n", "Текст:"]
    ),
    "balanced": SummarizationConfig(
        temperature=0.5,
        top_p=0.9,
        max_tokens=4196,
        presence_penalty=0.5,
        frequency_penalty=0.3,
        # stop=["</summary>", "\n\n\n"]
    ),
    "creative": SummarizationConfig(
        temperature=0.8,
        top_p=0.95,
        max_tokens=600,
        presence_penalty=0.3,
        frequency_penalty=0.2,
        # stop=["</summary>", "\n\n\n"]
    ),
}


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

    # # Batch-обробка
    # print("="*50)
    # print("📦 Тест batch-обробки")
    # print("="*50 + "\n")

    # batch_texts = news_headlines
    # # batch_texts = texts

    # sample_texts = texts
    # iteration_count = 1
    # for i in range(iteration_count):
    #     print(f"🫧 Iteration {i+1}/{iteration_count}\n{'*'*50}")
    #     start_time = time.time()

    #     batch_results = client.summarize_batch(
    #         texts=batch_texts,
    #         config="balanced",
    #         show_progress=True
    #         # custom_instruction=prompt
    #     )
    #     end_time = time.time()

    #     # Виведення результатів batch
    #     for i, result in enumerate(batch_results, 1):
    #         print(f"📄 Текст #{i}:")
    #         print(f"✨ Резюме: {result['summary']}\n")
    #         print(f"✳️ Причина зупинки:")
    #         print(f"{result['finish_reason']}\n")
    #     print(f"⏱️ Відповідь зайняла {end_time - start_time:.4f} секунд\n")
