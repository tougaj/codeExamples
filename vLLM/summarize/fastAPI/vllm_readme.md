# 🚀 vLLM FastAPI Server

FastAPI сервер для роботи з vLLM моделями з підтримкою перекладу, резюме та довільної генерації тексту.

## 📋 Особливості

- ✅ Batch inference для ефективної обробки
- 🔄 Переклад текстів українською
- 📝 Створення резюме новин
- 💬 Довільна генерація з chat template
- 📊 Детальна статистика токенів
- 🏥 Health check ендпоінт
- ⚡ Підтримка GPU з оптимізаціями vLLM

## 🛠️ Встановлення

### 1. Клонування та встановлення залежностей

```bash
# Створення віртуального оточення (опціонально)
python -m venv venv
source venv/bin/activate  # для Ubuntu

# Встановлення залежностей
pip install -r requirements.txt
```

### 2. Налаштування конфігурації

Створи файл `.env` на основі `.env.example`:

```bash
cp .env.example .env
```

Відредагуй `.env` під свої потреби:

```env
MODEL_NAME=google/gemma-3-4b-it
MAX_MODEL_LEN=8192
GPU_MEMORY_UTILIZATION=0.9
PORT=8000
```

## 🚀 Запуск

### Developer режим (з auto-reload)

```bash
# Встанови RELOAD=true в .env або:
RELOAD=true python main.py

# Або через uvicorn напряму:
uv run uvicorn fastAPI.main:app --reload --host 0.0.0.0 --port 8000
```

### Production режим

```bash
# Запуск через Python
python main.py

# Або через uvicorn з оптимізаціями:
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 1 \
  --log-level info
```

**⚠️ Примітка:** Для production краще використовувати `--workers 1`, оскільки vLLM модель займає багато пам'яті GPU. Якщо треба більше workers, використовуй load balancer з декількома інстансами.

### Production з Gunicorn + Uvicorn workers

```bash
pip install gunicorn

gunicorn main:app \
  --workers 1 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300 \
  --log-level info
```

## 📍 API Ендпоінти

### Health Check

```bash
GET /health
```

**Відповідь:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "google/gemma-3-4b-it",
  "max_model_len": 8192,
  "gpu_memory_utilization": 0.9
}
```

### 1. Переклад текстів

```bash
POST /translate
```

**Запит:**
```json
{
  "texts": [
    "Hello world! This is a test.",
    "Machine learning is amazing."
  ],
  "sampling_params": {
    "temperature": 0.1,
    "top_p": 0.9,
    "max_tokens": 8192
  }
}
```

**Відповідь:**
```json
{
  "results": [
    {
      "text": "Привіт, світ! Це тест.",
      "finish_reason": "stop",
      "input_tokens": 45,
      "output_tokens": 12
    }
  ],
  "total_texts": 2,
  "processing_time": 1.2345,
  "avg_input_tokens": 42.5,
  "avg_output_tokens": 10.5,
  "total_input_tokens": 85,
  "total_output_tokens": 21
}
```

### 2. Резюме текстів

```bash
POST /summarize
```

**Запит:**
```json
{
  "texts": [
    "Long article text here..."
  ],
  "sampling_params": {
    "temperature": 0.5,
    "max_tokens": 400
  }
}
```

### 3. Довільна генерація (з chat template)

```bash
POST /generate
```

**Запит:**
```json
{
  "texts": [
    "Розкажи мені про штучний інтелект"
  ],
  "sampling_params": {
    "temperature": 0.7,
    "max_tokens": 512
  }
}
```

### 4. Пряма генерація (без chat template)

```bash
POST /generate-raw
```

**Запит:**
```json
{
  "texts": [
    "Complete this sentence: The future of AI is"
  ],
  "sampling_params": {
    "temperature": 0.8
  }
}
```

## 🧪 Тестування API

### Використання curl

```bash
# Health check
curl http://localhost:8000/health

# Переклад
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Hello, how are you?"],
    "sampling_params": {
      "temperature": 0.1,
      "max_tokens": 100
    }
  }'

# Резюме
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Your long text here..."]
  }'
```

### Використання Python

```python
import requests

url = "http://localhost:8000/translate"
data = {
    "texts": ["Hello world!"],
    "sampling_params": {
        "temperature": 0.1,
        "max_tokens": 100
    }
}

response = requests.post(url, json=data)
print(response.json())
```

## 📊 Параметри генерації (sampling_params)

Всі параметри опціональні, мають значення за замовчанням:

| Параметр | За замовчанням | Діапазон | Опис |
|----------|---------------|----------|------|
| `temperature` | 0.7 | 0.0 - 2.0 | Креативність (↑ = більше варіативності) |
| `top_p` | 0.9 | 0.0 - 1.0 | Nucleus sampling |
| `max_tokens` | 512 | 1 - 8192 | Макс. токенів у відповіді |
| `presence_penalty` | 0.0 | -2.0 - 2.0 | Штраф за повторення концепцій |
| `frequency_penalty` | 0.0 | -2.0 - 2.0 | Штраф за повторення слів |
| `stop` | null | - | Список стоп-токенів |

## ⚙️ Змінні оточення (.env)

| Змінна | За замовчанням | Опис |
|--------|---------------|------|
| `MODEL_NAME` | google/gemma-3-4b-it | Назва або шлях до моделі |
| `MAX_MODEL_LEN` | 8192 | Макс. довжина контексту |