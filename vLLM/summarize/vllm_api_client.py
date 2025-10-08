"""
🌐 Клієнт для роботи з vLLM OpenAI-compatible API
Використовує офіційну openai бібліотеку для summarization
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from openai import OpenAI

from common import news_headlines, texts


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


class VLLMSummarizerClient:
    """
    Клієнт для роботи з vLLM API для summarization
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        api_key: str = "EMPTY",  # vLLM за замовчуванням не потребує ключа
        model: str = "google/gemma-3-4b-it"
    ):
        """
        Args:
            base_url: URL vLLM сервера
            api_key: API ключ (якщо налаштований на сервері)
            model: Назва моделі
        """
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self.model = model

    def create_chat_messages(
        self,
        text: str,
        custom_instruction: Optional[str] = None
    ) -> List[Dict]:
        """
        Створення повідомлень для chat API
        """
        default_instruction = """Ти — система створення стислих новинних резюме.
Отримуєш текст статті з новинного джерела будь-якою мовою.
Твоє завдання — підготувати коротке резюме **українською мовою** (3–5 речень), дотримуючись таких правил:
1. **Передай головний зміст точно й стисло** — зосередься на ключових фактах, подіях і тезах.
2. Якщо в тексті є ці дані, **зазнач основних учасників, місце, час і причину події.**
3. **Уникай** другорядних деталей, прикладів, цитат, оцінних суджень і емоційного тону.
4. Дотримуйся **нейтрального, об’єктивного та інформативного стилю.**
5. Використовуй **природну, зрозумілу й граматично правильну** українську мову.
6. **У відповіді подай лише резюме** — без коментарів, пояснень, заголовків або форматування."""

        instruction = custom_instruction or default_instruction

        return [
            {
                "role": "user",
                "content": f"{instruction}\n\nТекст:\n{text}\n\nРезюме:"
            }
        ]

    def summarize_single(
        self,
        text: str,
        config: str = "balanced",
        custom_instruction: Optional[str] = None,
        stream: bool = False
    ) -> Dict:
        """
        Summarization одного тексту

        Args:
            text: Текст для summarization
            config: Конфігурація ('precise', 'balanced', 'creative')
            custom_instruction: Кастомна інструкція
            stream: Streaming режим

        Returns:
            Словник з результатом
        """
        cfg = CONFIGS.get(config, CONFIGS["balanced"])
        messages = self.create_chat_messages(text, custom_instruction)

        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=cfg.temperature,
                top_p=cfg.top_p,
                max_tokens=cfg.max_tokens,
                presence_penalty=cfg.presence_penalty,
                frequency_penalty=cfg.frequency_penalty,
                stop=cfg.stop,
                stream=stream,
            )

            if stream:
                # Для streaming режиму збираємо текст
                summary = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        summary += content
                        print(content, end="", flush=True)
                print()  # новий рядок після streaming
            else:
                summary = response.choices[0].message.content

            elapsed_time = time.time() - start_time

            return {
                "original_text": text,
                "summary": summary.strip(),
                "config": config,
                "elapsed_time": elapsed_time,
                "finish_reason": response.choices[0].finish_reason if not stream else "stop",
            }

        except Exception as e:
            return {
                "original_text": text,
                "summary": None,
                "error": str(e),
                "config": config,
            }

    def summarize_batch(
        self,
        texts: List[str],
        config: str = "balanced",
        custom_instruction: Optional[str] = None,
        show_progress: bool = True
    ) -> List[Dict]:
        """
        Batch-обробка текстів (послідовно через API)

        Args:
            texts: Список текстів
            config: Конфігурація
            custom_instruction: Кастомна інструкція
            show_progress: Показувати прогрес

        Returns:
            Список результатів
        """
        if show_progress:
            print(f"🔄 Обробка {len(texts)} текстів через API...")

        results = []
        start_time = time.time()

        for i, text in enumerate(texts, 1):
            if show_progress:
                print(f"📝 Обробка {i}/{len(texts)}...", end=" ")

            result = self.summarize_single(
                text=text,
                config=config,
                custom_instruction=custom_instruction,
                stream=False
            )
            results.append(result)

            if show_progress:
                if result.get("error"):
                    print(f"❌ Помилка: {result['error']}")
                else:
                    print(f"✅ ({result['elapsed_time']:.2f}s)")

        total_time = time.time() - start_time

        if show_progress:
            successful = sum(1 for r in results if not r.get("error"))
            print(f"\n✅ Завершено: {successful}/{len(texts)} успішно")
            print(f"⏱️  Загальний час: {total_time:.2f}s")
            print(f"📊 Середній час на текст: {total_time/len(texts):.2f}s\n")

        return results

    def check_health(self) -> bool:
        """
        Перевірка доступності сервера
        """
        try:
            models = self.client.models.list()
            print(f"✅ Сервер доступний")
            print(f"📦 Доступні моделі: {[m.id for m in models.data]}")
            return True
        except Exception as e:
            print(f"❌ Сервер недоступний: {e}")
            return False


# 📊 Приклади використання
if __name__ == "__main__":
    # 🔌 Ініціалізація клієнта
    client = VLLMSummarizerClient(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY",  # змінити якщо на сервері налаштована авторизація
    )

    # 🏥 Перевірка здоров'я сервера
    print("="*80)
    print("🏥 Перевірка підключення до сервера")
    print("="*80 + "\n")

    if not client.check_health():
        print("\n⚠️  Переконайся, що vLLM сервер запущений!")
        print("Запусти: bash start_vllm_server.sh")
        exit(1)

    # print("\n" + "="*80)
    # print("📝 Тест одиночного summarization")
    # print("="*80 + "\n")

    # # Тестовий текст
    # test_text = """Штучний інтелект (ШІ) — це галузь комп'ютерних наук, яка займається створенням
    # інтелектуальних машин, здатних виконувати завдання, що зазвичай потребують людського
    # інтелекту. Це включає такі здібності, як розпізнавання мови, прийняття рішень,
    # переклад мов та візуальне сприйняття. Сучасний ШІ використовує машинне навчання
    # та глибокі нейронні мережі для досягнення вражаючих результатів у різних сферах."""

    # result = client.summarize_single(
    #     text=test_text,
    #     config="balanced"
    # )

    # print(f"📄 Оригінальний текст:\n{test_text}\n")
    # print(f"✨ Резюме:\n{result['summary']}\n")
    # print(f"⏱️  Час: {result['elapsed_time']:.2f}s")
    # print(f"🏁 Finish reason: {result['finish_reason']}\n")

    # Тест streaming режиму
    # print("="*80)
    # print("🌊 Тест streaming режиму")
    # print("="*80 + "\n")

    # print("✨ Резюме (streaming):\n")
    # stream_result = client.summarize_single(
    #     text=test_text,
    #     config="balanced",
    #     stream=True
    # )
    # print()

    # Batch-обробка
    print("="*80)
    print("📦 Тест batch-обробки")
    print("="*80 + "\n")

    # batch_texts = [
    #     """Python є однією з найпопулярніших мов програмування у світі. Вона відома своєю
    #     простотою та читабельністю синтаксису, що робить її ідеальною для початківців.
    #     Python широко використовується в веб-розробці, науковому програмуванні, аналізі
    #     даних, штучному інтелекті та автоматизації.""",

    #     """Блокчейн — це розподілена база даних, яка зберігає записи про транзакції у вигляді
    #     ланцюжка блоків. Кожен блок містить криптографічний хеш попереднього блоку, що робить
    #     систему надзвичайно захищеною від підробки.""",
    # ]
    # batch_texts = news_headlines
    batch_texts = texts

    prompt = """Ти — професійний перекладач української мови.
Твоє завдання — перекласти отриманий текст українською **точно за змістом**, але **природно й виразно за формою**, дотримуючись таких правил:
1. Використовуй **граматично правильну, природну та стилістично доречну** українську мову.
2. **Не перекладай дослівно.** Уникай кальок, штучних зворотів і буквальних конструкцій — замінюй їх на природні українські відповідники або ідіоматичні вирази.
3. Використовуй українські лапки **«...»** замість іноземних варіантів („...“, "...", ‘...’ тощо), дотримуючись правил пунктуації.
4. За потреби застосовуй **форматування Markdown**:
   * заголовки (`#`, `##`),
   * списки,
   * **жирний** або *курсивний* текст,
   * цитати тощо.
5. Не додавай пояснень, коментарів, приміток чи службових фраз.
6. Якщо надано текст українською, або російською мовою, то перекладати його не потрібно. В такому разі просто виведи пустий рядок.
7. **У відповіді подавай лише перекладений текст.**"""

    sample_texts = texts
    iteration_count = 1
    for i in range(iteration_count):
        print(f"🫧 Iteration {i+1}/{iteration_count}\n{'*'*50}")
        start_time = time.time()

        batch_results = client.summarize_batch(
            texts=batch_texts,
            config="balanced",
            show_progress=True
            # custom_instruction=prompt
        )
        end_time = time.time()

        # Виведення результатів batch
        for i, result in enumerate(batch_results, 1):
            print(f"📄 Текст #{i}:")
            print(f"✨ Резюме: {result['summary']}\n")
            print(f"✳️ Причина зупинки:")
            print(f"{result['finish_reason']}\n")
        print(f"⏱️ Відповідь зайняла {end_time - start_time:.4f} секунд\n")

    # Тест різних конфігурацій
    # print("="*80)
    # print("🎯 Порівняння різних конфігурацій")
    # print("="*80 + "\n")

    # for config_name in ["precise", "balanced", "creative"]:
    #     print(f"--- Конфігурація: {config_name.upper()} ---")
    #     result = client.summarize_single(
    #         text=test_text,
    #         config=config_name
    #     )
    #     print(f"✨ {result['summary']}\n")

    # # Кастомна інструкція
    # print("="*80)
    # print("🎨 Тест з кастомною інструкцією")
    # print("="*80 + "\n")

    # custom_result = client.summarize_single(
    #     text=test_text,
    #     config="balanced",
    #     custom_instruction="Створи резюме у форматі: 'Головна ідея: ... Застосування: ...'"
    # )

    # print(f"✨ Кастомне резюме:\n{custom_result['summary']}")
