"""
Варіант A: Використання вбудованого токенайзера vLLM
Простіший підхід, рекомендується для більшості випадків
"""

from vllm import LLM, SamplingParams
from typing import List

# 🔧 Ініціалізація моделі
llm = LLM(
    model="google/gemma-2-4b-it",  # або шлях до локальної моделі
    trust_remote_code=True,
    max_model_len=8192,  # максимальна довжина контексту
    gpu_memory_utilization=0.9,  # використання GPU пам'яті
)

# 📝 Отримання токенайзера з vLLM
tokenizer = llm.get_tokenizer()

# ⚙️ Параметри генерації для summarization
sampling_params = SamplingParams(
    temperature=0.3,  # низька для більш детермінованих резюме
    top_p=0.9,  # nucleus sampling
    max_tokens=200,  # максимум токенів для резюме
    presence_penalty=0.5,  # знижує повторення концепцій
    frequency_penalty=0.3,  # знижує повторення слів
    stop=["</summary>", "\n\n\n"],  # стоп-токени
)


def prepare_chat_prompt(text: str) -> str:
    """
    Підготовка промпту з використанням chat template
    """
    messages = [
        {
            "role": "user",
            "content": f"""Створи стисле резюме наступного тексту українською мовою. 
Резюме має бути чітким, інформативним та не перевищувати 3-4 речення.

Текст:
{text}

Резюме:"""
        }
    ]
    
    # 🎯 Застосування chat template
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,  # повертаємо string, не токени
        add_generation_prompt=True  # додає prompt для генерації відповіді
    )
    
    return prompt


def summarize_texts(texts: List[str]) -> List[str]:
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
    summaries = [output.outputs[0].text.strip() for output in outputs]
    
    return summaries


# 📊 Приклад використання
if __name__ == "__main__":
    # Тестові тексти
    sample_texts = [
        """Штучний інтелект (ШІ) — це галузь комп'ютерних наук, яка займається створенням 
        інтелектуальних машин, здатних виконувати завдання, що зазвичай потребують людського 
        інтелекту. Це включає такі здібності, як розпізнавання мови, прийняття рішень, 
        переклад мов та візуальне сприйняття. Сучасний ШІ використовує машинне навчання 
        та глибокі нейронні мережі для досягнення вражаючих результатів у різних сферах.""",
        
        """Python є однією з найпопулярніших мов програмування у світі. Вона відома своєю 
        простотою та читабельністю синтаксису, що робить її ідеальною для початківців. 
        Python широко використовується в веб-розробці, науковому програмуванні, аналізі 
        даних, штучному інтелекті та автоматизації. Велика кількість бібліотек та активна 
        спільнота роблять Python універсальним інструментом для розробників.""",
    ]
    
    print("🔄 Початок генерації резюме...\n")
    
    summaries = summarize_texts(sample_texts)
    
    # Виведення результатів
    for i, (original, summary) in enumerate(zip(sample_texts, summaries), 1):
        print(f"📄 Текст #{i}:")
        print(f"{original[:100]}...")
        print(f"\n✨ Резюме:")
        print(f"{summary}")
        print("\n" + "="*80 + "\n")
    
    # 📈 Статистика
    print(f"✅ Оброблено текстів: {len(sample_texts)}")
    print(f"📊 Середня довжина резюме: {sum(len(s.split()) for s in summaries) / len(summaries):.1f} слів")
