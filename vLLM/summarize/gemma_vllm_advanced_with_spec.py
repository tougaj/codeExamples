"""
🚀 Варіант B з Speculative Decoding
Target Model: Gemma 2 12B IT
Draft Model: Gemma 2 4B IT (для прискорення)

Speculative decoding може прискорити генерацію на 1.5-3x без втрати якості!
"""

from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
from typing import List, Dict, Optional
import time

# 🔧 Конфігурація моделей
TARGET_MODEL = "google/gemma-2-12b-it"  # основна модель (точна)
DRAFT_MODEL = "google/gemma-2-4b-it"     # draft модель (швидка)

# 📝 Ініціалізація LLM з speculative decoding
print("🔄 Завантаження моделей (це може зайняти хвилину)...")
print(f"🎯 Target model: {TARGET_MODEL}")
print(f"⚡ Draft model: {DRAFT_MODEL}")

llm = LLM(
    model=TARGET_MODEL,
    trust_remote_code=True,
    max_model_len=8192,
    gpu_memory_utilization=0.85,  # трохи менше, бо дві моделі
    tensor_parallel_size=1,
    
    # 🚀 SPECULATIVE DECODING параметри
    speculative_model=DRAFT_MODEL,  # draft модель для генерації кандидатів
    num_speculative_tokens=5,  # скільки токенів генерує draft за раз (3-5 оптимально)
    use_v2_block_manager=True,  # покращений memory manager для spec decoding
    enable_chunked_prefill=True,  # для ефективної роботи з довгими промптами
)

print("✅ Моделі завантажено!\n")

# 📝 Завантаження токенайзера (для target моделі)
tokenizer = AutoTokenizer.from_pretrained(
    TARGET_MODEL,
    trust_remote_code=True,
)

# ⚙️ Конфігурація параметрів для summarization
# Налаштував під speculative decoding
SUMMARIZATION_CONFIGS = {
    "precise": SamplingParams(
        temperature=0.2,
        top_p=0.85,
        max_tokens=150,
        presence_penalty=0.6,
        frequency_penalty=0.4,
        stop=["</summary>", "\n\n\n", "Текст:"],
        # Для spec decoding можна додати:
        use_beam_search=False,  # beam search несумісний зі spec decoding
    ),
    "balanced": SamplingParams(
        temperature=0.5,
        top_p=0.9,
        max_tokens=200,
        presence_penalty=0.5,
        frequency_penalty=0.3,
        stop=["</summary>", "\n\n\n"],
    ),
    "creative": SamplingParams(
        temperature=0.8,
        top_p=0.95,
        max_tokens=250,
        presence_penalty=0.3,
        frequency_penalty=0.2,
        stop=["</summary>", "\n\n\n"],
    ),
}


class GemmaSpeculativeSummarizer:
    """
    Summarizer з speculative decoding для максимальної швидкості
    """
    
    def __init__(self, llm_instance, tokenizer_instance):
        self.llm = llm_instance
        self.tokenizer = tokenizer_instance
        self.total_tokens_generated = 0
        self.total_time = 0.0
    
    def create_chat_messages(self, text: str, custom_instruction: str = None) -> List[Dict]:
        """Створення повідомлень для chat template"""
        default_instruction = """Створи стисле резюме наступного тексту українською мовою. 
Резюме має бути чітким, інформативним та не перевищувати 3-4 речення."""
        
        instruction = custom_instruction or default_instruction
        
        messages = [
            {
                "role": "user",
                "content": f"{instruction}\n\nТекст:\n{text}\n\nРезюме:"
            }
        ]
        
        return messages
    
    def apply_chat_template(self, messages: List[Dict]) -> str:
        """Застосування chat template через HF токенайзер"""
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        return prompt
    
    def summarize_batch(
        self, 
        texts: List[str], 
        config: str = "balanced",
        custom_instruction: str = None,
        show_progress: bool = True,
        show_speedup: bool = True,
    ) -> List[Dict]:
        """
        Batch-обробка з speculative decoding
        
        Args:
            texts: Список текстів
            config: Конфігурація ('precise', 'balanced', 'creative')
            custom_instruction: Кастомна інструкція
            show_progress: Показувати прогрес
            show_speedup: Показувати статистику прискорення
        """
        if show_progress:
            print(f"🔄 Підготовка {len(texts)} текстів для speculative decoding...")
        
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
            print(f"🚀 Генерація з speculative decoding (config: {config})...")
            print(f"⚡ Draft model генерує кандидати, target model верифікує")
        
        # 🎯 Генерація зі speculative decoding
        outputs = self.llm.generate(prompts, sampling_params)
        
        # Обробка результатів
        results = []
        total_tokens = 0
        
        for i, output in enumerate(outputs):
            tokens_generated = len(output.outputs[0].token_ids)
            total_tokens += tokens_generated
            
            result = {
                "original_text": texts[i],
                "summary": output.outputs[0].text.strip(),
                "tokens_generated": tokens_generated,
                "finish_reason": output.outputs[0].finish_reason,
            }
            results.append(result)
        
        elapsed_time = time.time() - start_time
        self.total_tokens_generated += total_tokens
        self.total_time += elapsed_time
        
        if show_progress:
            print(f"✅ Завершено за {elapsed_time:.2f}s")
            print(f"📊 Швидкість: {len(texts)/elapsed_time:.2f} текстів/с")
            print(f"🔢 Токенів згенеровано: {total_tokens}")
            print(f"⚡ Швидкість генерації: {total_tokens/elapsed_time:.1f} токенів/с")
        
        if show_speedup:
            # Приблизна оцінка прискорення
            # Без spec decoding gemma-12b генерує ~20-30 tokens/s
            # З spec decoding очікуємо ~40-60 tokens/s (1.5-2.5x speedup)
            tokens_per_sec = total_tokens / elapsed_time
            estimated_baseline = 25  # baseline для gemma-12b без spec decoding
            speedup = tokens_per_sec / estimated_baseline
            
            print(f"\n💡 Оціночне прискорення: ~{speedup:.1f}x")
            print(f"   (порівняно з baseline ~{estimated_baseline} tokens/s)\n")
        
        return results
    
    def get_stats(self) -> Dict:
        """Отримати загальну статистику роботи"""
        if self.total_time == 0:
            return {"message": "Ще не було згенеровано жодного тексту"}
        
        return {
            "total_tokens_generated": self.total_tokens_generated,
            "total_time": self.total_time,
            "average_tokens_per_second": self.total_tokens_generated / self.total_time,
            "target_model": TARGET_MODEL,
            "draft_model": DRAFT_MODEL,
        }


# 📊 Приклад використання
if __name__ == "__main__":
    # Ініціалізація summarizer
    summarizer = GemmaSpeculativeSummarizer(llm, tokenizer)
    
    # Тестові тексти (більш довгі для демонстрації переваг spec decoding)
    sample_texts = [
        """Квантові комп'ютери використовують принципи квантової механіки для обробки інформації. 
        На відміну від класичних комп'ютерів, які працюють з бітами (0 або 1), квантові 
        комп'ютери використовують кубіти, які можуть перебувати в суперпозиції станів. 
        Це дозволяє їм виконувати певні обчислення експоненційно швидше за класичні системи. 
        Квантові комп'ютери мають потенціал революціонізувати криптографію, оптимізацію та 
        симуляцію молекулярних систем. Однак вони надзвичайно чутливі до шумів і потребують 
        екстремально низьких температур для роботи. Провідні компанії, такі як IBM, Google та 
        IonQ, активно працюють над створенням стабільних квантових систем.""",
        
        """Блокчейн — це розподілена база даних, яка зберігає записи про транзакції у вигляді 
        ланцюжка блоків. Кожен блок містить криптографічний хеш попереднього блоку, що робить 
        систему надзвичайно захищеною від підробки. Технологія блокчейн лежить в основі 
        криптовалют, але її застосування набагато ширше: від смарт-контрактів до систем 
        управління ланцюгами постачання. Ключовими перевагами є децентралізація, прозорість 
        та незмінність записів. Однак блокчейн має обмеження у швидкості обробки транзакцій 
        та споживає значну кількість енергії, особливо в мережах з proof-of-work алгоритмом.""",
        
        """Машинне навчання — це підгалузь штучного інтелекту, яка дозволяє системам 
        автоматично покращувати свою продуктивність через досвід. Замість явного програмування 
        правил, алгоритми машинного навчання виявляють патерни в даних. Існує три основні 
        типи: навчання з учителем, де модель тренується на міченних даних; навчання без учителя, 
        де модель знаходить структури в неміченних даних; та навчання з підкріпленням, де агент 
        вчиться через взаємодію з середовищем. Глибоке навчання, яке використовує нейронні мережі 
        з багатьма шарами, досягло вражаючих результатів у розпізнаванні зображень, обробці 
        природної мови та інших складних задачах.""",
    ]
    
    print("="*80)
    print("🎯 ТЕСТУВАННЯ SPECULATIVE DECODING")
    print("="*80)
    print(f"\n📦 Target Model: {TARGET_MODEL}")
    print(f"⚡ Draft Model: {DRAFT_MODEL}")
    print(f"🔢 Кількість speculative tokens: 5\n")
    
    # Тест balanced конфігурації
    print("="*80)
    print("📊 Тест: Balanced конфігурація")
    print("="*80 + "\n")
    
    results = summarizer.summarize_batch(
        texts=sample_texts,
        config="balanced",
        show_progress=True,
        show_speedup=True,
    )
    
    # Виведення результатів
    for i, result in enumerate(results, 1):
        print(f"📄 Текст #{i}:")
        print(f"Оригінал: {result['original_text'][:100]}...")
        print(f"\n✨ Резюме ({result['tokens_generated']} токенів):")
        print(f"{result['summary']}")
        print(f"🏁 Finish reason: {result['finish_reason']}")
        print("\n" + "-"*80 + "\n")
    
    # Порівняння конфігурацій
    print("="*80)
    print("🔬 Порівняння різних конфігурацій")
    print("="*80 + "\n")
    
    test_text = sample_texts[0]
    
    for config_name in ["precise", "balanced", "creative"]:
        print(f"--- {config_name.upper()} ---")
        result = summarizer.summarize_batch(
            texts=[test_text],
            config=config_name,
            show_progress=False,
            show_speedup=False,
        )[0]
        print(f"✨ {result['summary']}")
        print(f"📊 Токенів: {result['tokens_generated']}\n")
    
    # Загальна статистика
    print("="*80)
    print("📈 ЗАГАЛЬНА СТАТИСТИКА РОБОТИ")
    print("="*80 + "\n")
    
    stats = summarizer.get_stats()
    print(f"🔢 Всього токенів згенеровано: {stats['total_tokens_generated']}")
    print(f"⏱️  Загальний час: {stats['total_time']:.2f}s")
    print(f"⚡ Середня швидкість: {stats['average_tokens_per_second']:.1f} tokens/s")
    print(f"\n🎯 Target: {stats['target_model']}")
    print(f"⚡ Draft: {stats['draft_model']}")
    
    print("\n" + "="*80)
    print("💡 TIPS для оптимізації:")
    print("="*80)
    print("""
1. 📊 num_speculative_tokens: 
   - 3-5 оптимально для більшості задач
   - Більше = більше overhead, але потенційно швидше
   - Менше = менше overhead, але менше прискорення

2. 🎯 Вибір draft моделі:
   - Має бути з тієї ж родини (Gemma 2)
   - Співвідношення 1:3 (4B draft, 12B target) - оптимальне
   - Draft модель має використовувати той же словник

3. ⚙️ gpu_memory_utilization:
   - 0.85 для двох моделей (draft + target)
   - Якщо OOM - зменш до 0.75-0.8

4. 🚀 Для максимальної швидкості:
   - use_v2_block_manager=True
   - enable_chunked_prefill=True
   - Використовуй batch processing
    """)
