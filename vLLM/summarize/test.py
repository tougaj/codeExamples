#!/usr/bin/env python

import time
from typing import Optional

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

from common import texts

model = "google/gemma-3-4b-it"
# model = "google/gemma-3-12b-it"
# model = "mistralai/Mistral-7B-Instruct-v0.1"
llm = LLM(model=model,
          max_model_len=8192,  # максимальна довжина контексту
          gpu_memory_utilization=0.95,  # можна більше, бо одна модель
          swap_space=8,  # GB swap на CPU (якщо не вистачить VRAM)
          # ⚡PREFIX CACHING - ключова оптимізація!
          enable_prefix_caching=True,  # кешує системний промпт
          enable_chunked_prefill=True,  # ефективна обробка довгих промптів
          )
# tokenizer = llm.get_tokenizer()
tokenizer = AutoTokenizer.from_pretrained(model)


def process(
    prompt: str,
    text: str,
    max_new_tokens: Optional[int] = 8192,
    temperature=0.1,
):
    messages_list = [
        {
            "role": "user",
            "content": (f"{prompt}\n\n{text}"),
        }
    ]
    texts = tokenizer.apply_chat_template(
        messages_list,
        tokenize=False,
        add_generation_prompt=True,
    )

    # Generate outputs
    start_time = time.time()

    if max_new_tokens is None:
        word_count = len(text.split())
        # Українська трохи довша за французьку → множимо на 1.3
        estimated_tokens = int(word_count * 3) + 20  # + буфер
        max_new_tokens = max(100, estimated_tokens)  # обмеження
    print(f"📟 Max tokens: {max_new_tokens}")

    sampling_params = SamplingParams(
        temperature=temperature, top_p=0.95, max_tokens=max_new_tokens, n=1
    )

    outputs = llm.generate(texts, sampling_params)
    end_time = time.time()

    # Print the outputs.
    for output in outputs:
        # prompt = output.prompt
        for out in output.outputs:
            generated_text = out.text.strip()
            # print(f"📝 Prompt:\n{prompt!r},\n\n📤 Generated text:\n{generated_text!r}")
            # print(f"📤 Generated text:\n{generated_text!r}")
            print(f"📤 Generated text:\n{generated_text}")
        print(f"⏱️ Відповідь зайняла {end_time - start_time:.4f} секунд")


def summarize(text: str, max_new_tokens: Optional[int]):
    process(
        """Ти — система створення стислих новинних резюме.
Отримуєш текст статті з новинного джерела будь-якою мовою.
Твоє завдання — підготувати коротке резюме **українською мовою** (3–5 речень), дотримуючись таких правил:

1. **Передай головний зміст точно й стисло** — зосередься на ключових фактах, подіях і тезах.
2. Якщо в тексті є ці дані, **зазнач основних учасників, місце, час і причину події.**
3. **Уникай** другорядних деталей, прикладів, цитат, оцінних суджень і емоційного тону.
4. Дотримуйся **нейтрального, об’єктивного та інформативного стилю.**
5. Використовуй **природну, зрозумілу й граматично правильну** українську мову.
6. **У відповіді подай лише резюме** — без коментарів, пояснень, заголовків або форматування.
Текст для сумаризації:""",
        text,
        max_new_tokens=max_new_tokens,
        temperature=0.5,
    )


def translate(text: str):
    process(
        """Ти — професійний перекладач української мови.
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
7. **У відповіді подавай лише перекладений текст.**
Текст для перекладу:\n\n""",
        text,
    )


def complex_processing(text: str):
    process(
        """Ти — багатофункціональна система для обробки текстів. Твоє завдання:

1. **Визначення мови:**

   * Визнач мову оригінального тексту та віддай її у форматі **ISO 639-1** (наприклад: `uk`, `ru`, `en`, `fr`).

2. **Переклад (якщо потрібно):**

   * Якщо оригінальний текст **не українською і не російською**, переклади його українською мовою.
   * Переклад має:

     * бути природним і грамотним українським текстом ✍️
     * зберігати **структуру оригіналу** (заголовки, абзаци, списки, форматування) 🏗️
     * застосовувати Markdown там, де доречно 📑
     * замінювати лапки на українські («…») 📝
     * уникати кальки та зберігати природний стиль 🌿
   * У результаті включай поле `"translation"`.

3. **Винятки:**

   * Якщо текст **українською або російською**, перекладати його не потрібно і поле `"translation"` у результаті **не включати**.

4. **Сумаризація:**

   * У будь-якому випадку створи коротке резюме (3–5 речень) українською мовою, яке:

     * передає головні факти та тези 📰
     * зазначає учасників, час, місце та причини події (якщо є) 📍
     * зберігає нейтральний і стислий стиль ⚖️

**Формат результату (JSON):**

```json
{
  "lang_original": "xx",
  "translation": "Тут перекладений текст українською зі збереженням структури…",
  "summary": "Тут стислий виклад українською…"
}
```

> Якщо мова оригіналу — `uk` або `ru`, то поле `"translation"` не включати.

**Вхід:**

```
{Текст статті}
```

**Вихід:**
JSON з:

* `lang_original` (обов’язково)
* `summary` (обов’язково)
* `translation` (лише якщо мова ≠ `uk` і ≠ `ru`).
""",
        text,
    )


for text in texts:
    translate(text)
    # summarize(text, 300)
    # complex_processing(text)
    print('-'*50)
