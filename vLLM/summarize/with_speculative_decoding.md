Чудово! Тоді оновлюю скрипт з вбудованим speculative decoding vLLM 🚀Готово! 🎉 Ось що я оновив:

## 🚀 Ключові зміни для Speculative Decoding:

### 1️⃣ **Конфігурація моделей**
```python
TARGET_MODEL = "google/gemma-2-12b-it"  # 12B - точна
DRAFT_MODEL = "google/gemma-2-4b-it"     # 4B - швидка
```

### 2️⃣ **Параметри LLM з spec decoding**
```python
llm = LLM(
    model=TARGET_MODEL,
    speculative_model=DRAFT_MODEL,        # 🎯 draft модель
    num_speculative_tokens=5,             # ⚡ 5 токенів за раз
    use_v2_block_manager=True,            # 💾 покращений memory
    enable_chunked_prefill=True,          # 🚀 для довгих промптів
    gpu_memory_utilization=0.85,          # трохи менше для двох моделей
)
```

### 3️⃣ **Покращена статистика**
- 📊 Швидкість генерації (tokens/s)
- 💡 Оціночне прискорення (~1.5-2.5x)
- 📈 Загальна статистика роботи

## 🎯 Як це працює:

1. **Draft model (4B)** швидко генерує 5 токенів-кандидатів
2. **Target model (12B)** верифікує їх паралельно за один прохід
3. Приймаються всі правильні токени → прискорення!
4. Якщо щось не так → target генерує сама

## ⚡ Очікувані результати:

- **Без spec decoding:** ~20-30 tokens/s (Gemma 12B)
- **З spec decoding:** ~40-60 tokens/s (1.5-2.5x швидше!)
- **Якість:** абсолютно ідентична (математично гарантовано)

## 💾 Вимоги до пам'яті:

- **Gemma 12B:** ~24GB VRAM
- **Gemma 4B:** ~8GB VRAM  
- **Разом:** ~32GB VRAM (одна GPU) або 2x GPU з меншою пам'яттю

Якщо виникне OOM - зменш `gpu_memory_utilization` до 0.75! 💪
