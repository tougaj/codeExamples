"""
Варіант B: Використання окремого HuggingFace токенайзера
Більше контролю та гнучкості, корисно для кастомізації
"""

import time
from typing import Dict, List

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

from common import texts

# 🔧 Ініціалізація моделі
# MODEL_NAME = "google/gemma-3-4b-it"
MODEL_NAME = "google/gemma-3-12b-it"

llm = LLM(
    model=MODEL_NAME,
    trust_remote_code=True,
    max_model_len=1024,
    # max_model_len=8192,
    gpu_memory_utilization=0.95,
    tensor_parallel_size=1,  # для мульти-GPU збільш це значення
)

# 📝 Завантаження токенайзера з HuggingFace окремо
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
)

# ⚙️ Конфігурація параметрів для різних типів summarization
SUMMARIZATION_CONFIGS = {
    "precise": SamplingParams(
        temperature=0.2,  # дуже детерміновано
        top_p=0.85,
        max_tokens=400,
        presence_penalty=0.6,
        frequency_penalty=0.4,
        stop=["</summary>", "\n\n\n", "Текст:"],
    ),
    "balanced": SamplingParams(
        temperature=0.5,  # баланс креативності та точності
        top_p=0.9,
        max_tokens=600,
        presence_penalty=0.5,
        frequency_penalty=0.3,
        stop=["</summary>", "\n\n\n"],
    ),
    "creative": SamplingParams(
        temperature=0.8,  # більш креативні резюме
        top_p=0.95,
        max_tokens=800,
        presence_penalty=0.3,
        frequency_penalty=0.2,
        stop=["</summary>", "\n\n\n"],
    ),
}


class GemmaSummarizer:
    """
    Клас для зручної роботи з summarization через vLLM
    """

    def __init__(self, llm_instance, tokenizer_instance):
        self.llm = llm_instance
        self.tokenizer = tokenizer_instance

    def create_chat_messages(self, text: str, custom_instruction: str = None) -> List[Dict]:
        """
        Створення повідомлень для chat template
        """
        # default_instruction = """Створи стисле резюме наступного тексту українською мовою.
# Резюме має бути чітким, інформативним та не перевищувати 3-4 речення."""
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

        messages = [
            {
                "role": "user",
                "content": f"{instruction}\n\nТекст:\n{text}\n\nРезюме:"
            }
        ]

        return messages

    def apply_chat_template(self, messages: List[Dict]) -> str:
        """
        Застосування chat template через HF токенайзер
        """
        # 🎯 Використання apply_chat_template з токенайзера
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,  # повертаємо string
            add_generation_prompt=True,  # додаємо generation prompt
        )

        return prompt

    def summarize_batch(
        self,
        texts: List[str],
        config: str = "balanced",
        custom_instruction: str = None,
        show_progress: bool = True
    ) -> List[Dict]:
        """
        Batch-обробка текстів з детальною інформацією

        Args:
            texts: Список текстів
            config: Конфігурація ('precise', 'balanced', 'creative')
            custom_instruction: Кастомна інструкція для моделі
            show_progress: Показувати прогрес

        Returns:
            Список словників з результатами
        """
        if show_progress:
            print(f"🔄 Підготовка {len(texts)} текстів...")

        start_time = time.time()

        # Підготовка промптів
        prompts = []
        for text in texts:
            messages = self.create_chat_messages(text, custom_instruction)
            prompt = self.apply_chat_template(messages)
            prompts.append(prompt)

        # Вибір параметрів
        sampling_params = SUMMARIZATION_CONFIGS.get(config, SUMMARIZATION_CONFIGS["balanced"])

        if show_progress:
            print(f"🚀 Генерація резюме (config: {config})...")

        # Генерація
        outputs = self.llm.generate(prompts, sampling_params)

        # Обробка результатів
        results = []
        for i, output in enumerate(outputs):
            result = {
                "original_text": texts[i],
                "summary": output.outputs[0].text.strip(),
                "tokens_generated": len(output.outputs[0].token_ids),
                "finish_reason": output.outputs[0].finish_reason,
            }
            results.append(result)

        elapsed_time = time.time() - start_time

        if show_progress:
            print(f"✅ Завершено за {elapsed_time:.2f}s")
            print(f"📊 Швидкість: {len(texts)/elapsed_time:.2f} текстів/с\n")

        return results


# 📊 Приклад використання
if __name__ == "__main__":
    # Ініціалізація summarizer
    summarizer = GemmaSummarizer(llm, tokenizer)

    # Тестові тексти
    # sample_texts = [
    #     """Квантові комп'ютери використовують принципи квантової механіки для обробки інформації.
    #     На відміну від класичних комп'ютерів, які працюють з бітами (0 або 1), квантові
    #     комп'ютери використовують кубіти, які можуть перебувати в суперпозиції станів.
    #     Це дозволяє їм виконувати певні обчислення експоненційно швидше за класичні системи.
    #     Квантові комп'ютери мають потенціал революціонізувати криптографію, оптимізацію та
    #     симуляцію молекулярних систем.""",

    #     """Блокчейн — це розподілена база даних, яка зберігає записи про транзакції у вигляді
    #     ланцюжка блоків. Кожен блок містить криптографічний хеш попереднього блоку, що робить
    #     систему надзвичайно захищеною від підробки. Технологія блокчейн лежить в основі
    #     криптовалют, але її застосування набагато ширше: від смарт-контрактів до систем
    #     управління ланцюгами постачання.""",

    #     """Машинне навчання — це підгалузь штучного інтелекту, яка дозволяє системам
    #     автоматично покращувати свою продуктивність через досвід. Замість явного програмування
    #     правил, алгоритми машинного навчання виявляють патерни в даних. Існує три основні
    #     типи: навчання з учителем, без учителя та з підкріпленням.""",
    # ]
    sample_texts = texts

    # Тестування різних конфігурацій
    for config_name in ["precise", "balanced", "creative"]:
        print(f"\n{'='*80}")
        print(f"🎯 Тестування конфігурації: {config_name.upper()}")
        print(f"{'='*80}\n")

        results = summarizer.summarize_batch(
            texts=sample_texts,
            config=config_name,
            show_progress=True
        )

        # Виведення результатів
        for i, result in enumerate(results, 1):
            print(f"📄 Текст #{i} ({result['tokens_generated']} токенів):")
            print(f"✨ Резюме: {result['summary']}")
            print(f"🏁 Finish reason: {result['finish_reason']}\n")

    # Приклад з кастомною інструкцією
    print(f"\n{'='*80}")
    print(f"🎨 Тест з кастомною інструкцією")
    print(f"{'='*80}\n")

    custom_results = summarizer.summarize_batch(
        texts=[sample_texts[0]],
        config="balanced",
        custom_instruction="Створи резюме цього тексту у форматі: 'Ключова ідея: ... Практичне застосування: ...'",
        show_progress=True
    )

    print(f"✨ Кастомне резюме:\n{custom_results[0]['summary']}")
