"""
Варіант A: Використання вбудованого токенайзера vLLM
Простіший підхід, рекомендується для більшості випадків
"""

# import json
import time
from typing import List

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

from common import news_headlines, texts

# MODEL_NAME = "google/gemma-2-2b-it"
MODEL_NAME = "google/gemma-3-4b-it"
# MODEL_NAME = "google/gemma-3-12b-it"
# MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

# 🔧 Ініціалізація моделі
llm = LLM(
    model=MODEL_NAME,  # або шлях до локальної моделі
    # trust_remote_code=True,
    max_model_len=8192,  # максимальна довжина контексту for 4b
    # max_model_len=900,  # максимальна довжина контексту for 12b
    gpu_memory_utilization=0.5,  # використання GPU пам'яті
    tensor_parallel_size=1,  # для мульти-GPU збільш це значення
    # dtype="bfloat16"
    max_num_seqs=15,  # максимум паралельних запитів (10 + запас)
    swap_space=8,  # GB swap на CPU (якщо не вистачить VRAM)
    enable_prefix_caching=True,  # кешує системний промпт
    enable_chunked_prefill=True,  # ефективна обробка довгих промптів
    # max_num_batched_tokens_prefill=8192,  # розмір чанків для prefill
    dtype="auto",  # автовизначення (float16/bfloat16)
)
# Дозволяє побачити параметри моделі, зокрема квантизацію
# print(json.dumps(llm.llm_engine.model_config.__dict__, indent=2, default=str))

# 📝 Отримання токенайзера з vLLM
# tokenizer = llm.get_tokenizer()
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
)

# ⚙️ Параметри генерації для summarization
sampling_params = SamplingParams(
    temperature=0.5,  # низька для більш детермінованих резюме
    # temperature=0.1,  # низька для більш точних перекладів
    top_p=0.9,  # nucleus sampling
    max_tokens=400,  # максимум токенів для резюме
    # max_tokens=8192,  # максимум токенів для перекладу
    presence_penalty=0.5,  # знижує повторення концепцій
    frequency_penalty=0.3,  # знижує повторення слів
    # stop=["</summary>", "\n\n\n"],  # стоп-токени
)


def prepare_chat_prompt(text: str) -> str:
    """
    Підготовка промпту з використанням chat template
    """
    # messages = [
    #     {
    #         "role": "user",
    #         "content": f"""Ти — професійний перекладач української мови.
    # Твоє завдання — перекласти отриманий текст українською **точно за змістом**, але **природно й виразно за формою**, дотримуючись таких правил:
    # 1. Використовуй **граматично правильну, природну та стилістично доречну** українську мову.
    # 2. **Не перекладай дослівно.** Уникай кальок, штучних зворотів і буквальних конструкцій — замінюй їх на природні українські відповідники або ідіоматичні вирази.
    # 3. Використовуй українські лапки **«...»** замість іноземних варіантів („...“, "...", ‘...’ тощо), дотримуючись правил пунктуації.
    # 4. За потреби застосовуй **форматування Markdown**:
    #    * заголовки (`#`, `##`),
    #    * списки,
    #    * **жирний** або *курсивний* текст,
    #    * **жирний** текст для іменованих сутностей (NER),
    #    * цитати тощо.
    # 5. Не додавай пояснень, коментарів, приміток чи службових фраз.
    # 6. Якщо надано текст українською, або російською мовою, то перекладати його не потрібно. В такому разі просто виведи пустий рядок.
    # 7. **У відповіді подавай лише перекладений текст.**
    # Текст для перекладу:\n\n{text}""",
    #     }
    # ]
    messages = [
        {
            "role": "user",
            "content": f"""Ти — система створення стислих новинних резюме.
Отримуєш текст статті з новинного джерела будь-якою мовою.
Твоє завдання — підготувати коротке резюме **українською мовою** (3–5 речень), дотримуючись таких правил:
1. Резюме має **обов'язково** бути українською мовою!.
2. **Передай головний зміст точно й стисло** — зосередься на ключових фактах, подіях і тезах.
3. Якщо в тексті є ці дані, **зазнач основних учасників, місце, час і причину події.**
4. **Уникай** другорядних деталей, прикладів, цитат, оцінних суджень і емоційного тону.
5. Дотримуйся **нейтрального, об’єктивного та інформативного стилю.**
6. Використовуй **природну, зрозумілу й граматично правильну** українську мову.
7. Використовуй Markdown **жирний** текст для іменованих сутностей (NER).
8. **У відповіді подай лише резюме** — без коментарів, пояснень, заголовків або форматування.
Текст для резюме:\n\n{text}""",
        }
    ]
#     messages = [
#         {
#             "role": "user",
#             "content": f"""Створи стисле резюме наступного тексту українською мовою.
# Резюме має бути чітким, інформативним та не перевищувати 3-4 речення.

# Текст:
# {text}

# Резюме:""",
#         }
#     ]

    # 🎯 Застосування chat template
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,  # повертаємо string, не токени
        add_generation_prompt=True,  # додає prompt для генерації відповіді
    )
    # print(prompt)

    return prompt


def summarize_texts(texts: List[str]) -> list[tuple[str, str | None]]:
    """
    Batch-обробка текстів для створення резюме

    Args:
        texts: Список текстів для summarization

    Returns:
        Список згенерованих резюме
    """
    # Підготовка всіх промптів
    prompts = [prepare_chat_prompt(text) for text in texts]

    # 🚀 Batch inference
    outputs = llm.generate(prompts, sampling_params)

    # Extraction результатів
    summaries = [(output.outputs[0].text.strip(), output.outputs[0].finish_reason) for output in outputs]

    return summaries


def process(texts: list[str]):
    print("🔄 Початок генерації резюме...\n")

    start_time = time.time()
    summaries = summarize_texts(texts)
    end_time = time.time()

    # Виведення результатів
    for i, (original, summary) in enumerate(zip(texts, summaries), 1):
        (text, reason) = summary
        print(f"📄 Текст #{i}:")
        print(f"{original[:100]}...")
        print(f"\n✨ Резюме:")
        print(f"{text}")
        print(f"\n✳️ Причина зупинки:")
        print(f"{reason}")
        print("\n" + "=" * 80 + "\n")

    # 📈 Статистика
    print(f"✅ Оброблено текстів: {len(sample_texts)}")
    print(
        f"📊 Середня довжина резюме: {sum(len(s[0].split()) for s in summaries) / len(summaries):.1f} слів"
    )
    print(f"⏱️ Відповідь зайняла {end_time - start_time:.4f} секунд")


# 📊 Приклад використання
if __name__ == "__main__":
    # Тестові тексти
    # sample_texts = [
    #     """Штучний інтелект (ШІ) — це галузь комп'ютерних наук, яка займається створенням
    #     інтелектуальних машин, здатних виконувати завдання, що зазвичай потребують людського
    #     інтелекту. Це включає такі здібності, як розпізнавання мови, прийняття рішень,
    #     переклад мов та візуальне сприйняття. Сучасний ШІ використовує машинне навчання
    #     та глибокі нейронні мережі для досягнення вражаючих результатів у різних сферах.""",

    #     """Python є однією з найпопулярніших мов програмування у світі. Вона відома своєю
    #     простотою та читабельністю синтаксису, що робить її ідеальною для початківців.
    #     Python широко використовується в веб-розробці, науковому програмуванні, аналізі
    #     даних, штучному інтелекті та автоматизації. Велика кількість бібліотек та активна
    #     спільнота роблять Python універсальним інструментом для розробників.""",
    # ]
    sample_texts = texts
    iteration_count = 1
    for i in range(iteration_count):
        print(f"\n\n🫧 Iteration {i+1}/{iteration_count}\n{'*'*50}")
        process(sample_texts)

    # print("🔄 Початок генерації резюме...\n")

    # start_time = time.time()
    # summaries = summarize_texts(sample_texts)
    # end_time = time.time()

    # # Виведення результатів
    # for i, (original, summary) in enumerate(zip(sample_texts, summaries), 1):
    #     (text, reason) = summary
    #     print(f"📄 Текст #{i}:")
    #     print(f"{original[:100]}...")
    #     print(f"\n✨ Резюме:")
    #     print(f"{text}")
    #     print(f"\n✳️ Причина зупинки:")
    #     print(f"{reason}")
    #     print("\n" + "=" * 80 + "\n")

    # # 📈 Статистика
    # print(f"✅ Оброблено текстів: {len(sample_texts)}")
    # print(
    #     f"📊 Середня довжина резюме: {sum(len(s[0].split()) for s in summaries) / len(summaries):.1f} слів"
    # )
    # print(f"⏱️ Відповідь зайняла {end_time - start_time:.4f} секунд")
