# 🚀 Quick Start Guide: vLLM API для Gemma 3

## 📦 Встановлення залежностей

```bash
# vLLM (якщо ще не встановлено)
pip install vllm

# OpenAI Python SDK для клієнта
pip install openai

# Опціонально: для моніторингу
pip install httpx
```

## 🎬 Крок 1: Запуск сервера

### Варіант A: Через bash скрипт (рекомендовано)
```bash
# Зроби скрипт виконуваним
chmod +x start_vllm_server.sh

# Запусти сервер
./start_vllm_server.sh
```

### Варіант B: Пряма команда
```bash
vllm serve google/gemma-2-4b-it \
    --host 0.0.0.0 \
    --port 8000 \
    --trust-remote-code \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.9
```

### Варіант C: З авторизацією
```bash
vllm serve google/gemma-2-4b-it \
    --host 0.0.0.0 \
    --port 8000 \
    --api-key "your-secret-api-key-here" \
    --trust-remote-code
```

**Сервер буде доступний на:**
- API: `http://localhost:8000/v1`
- Документація: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

---

## 🧪 Крок 2: Тестування через curl

### Перевірка здоров'я
```bash
curl http://localhost:8000/health
```

### Список моделей
```bash
curl http://localhost:8000/v1/models
```

### Простий запит на summarization
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/gemma-2-4b-it",
    "messages": [
      {
        "role": "user",
        "content": "Створи коротке резюме: Python - це мова програмування високого рівня."
      }
    ],
    "temperature": 0.5,
    "max_tokens": 100
  }'
```

### З streaming
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/gemma-2-4b-it",
    "messages": [{"role": "user", "content": "Резюме про Python"}],
    "stream": true
  }'
```

---

## 🐍 Крок 3: Використання Python клієнта

### Базове використання
```python
from vllm_api_client import VLLMSummarizerClient

# Ініціалізація
client = VLLMSummarizerClient()

# Перевірка підключення
client.check_health()

# Одиночне summarization
result = client.summarize_single(
    text="Ваш текст тут...",
    config="balanced"
)
print(result['summary'])
```

### Batch-обробка
```python
texts = ["текст 1", "текст 2", "текст 3"]
results = client.summarize_batch(texts, config="precise")

for r in results:
    print(r['summary'])
```

### Streaming режим
```python
result = client.summarize_single(
    text="Ваш текст...",
    stream=True  # Виводить текст поступово
)
```

---

## ⚙️ Конфігурації

### Precise (точне резюме)
- Temperature: 0.2 (мало креативності)
- Max tokens: 150
- Використовуй для: фактичних текстів, новин

### Balanced (збалансоване)
- Temperature: 0.5
- Max tokens: 200
- Використовуй для: загальних текстів

### Creative (креативне)
- Temperature: 0.8
- Max tokens: 250
- Використовуй для: художніх текстів, есеїв

---

## 🔧 Налаштування для продакшену

### Systemd service (автозапуск)
```bash
# Створи /etc/systemd/system/vllm.service
[Unit]
Description=vLLM API Server
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/your/project
ExecStart=/usr/local/bin/vllm serve google/gemma-2-4b-it --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Активація
sudo systemctl enable vllm
sudo systemctl start vllm
sudo systemctl status vllm
```

### Docker (альтернатива)
```dockerfile
FROM vllm/vllm-openai:latest

ENV MODEL_NAME=google/gemma-2-4b-it
ENV PORT=8000

CMD ["vllm", "serve", "${MODEL_NAME}", "--host", "0.0.0.0", "--port", "${PORT}"]
```

---

## 📊 Моніторинг та метрики

### Prometheus метрики
```bash
curl http://localhost:8000/metrics
```

### Логи
```bash
# Дивитись логи в реальному часі
journalctl -u vllm -f

# Або якщо запущено вручну
tail -f vllm.log
```

---

## 🐛 Troubleshooting

### Сервер не запускається
```bash
# Перевір доступність GPU
nvidia-smi

# Перевір що порт вільний
netstat -tulpn | grep 8000

# Зменш використання пам'яті
vllm serve google/gemma-2-4b-it --gpu-memory-utilization 0.7
```

### Out of Memory
```bash
# Використай квантизацію
vllm serve google/gemma-2-4b-it --quantization awq

# Або зменш max-model-len
vllm serve google/gemma-2-4b-it --max-model-len 4096
```

### Повільна генерація
```bash
# Увімкни prefix caching
vllm serve google/gemma-2-4b-it --enable-prefix-caching

# Або збільш batch size
vllm serve google/gemma-2-4b-it --max-num-seqs 256
```

---

## 🔐 Безпека

### Додати API key
```python
# При запуску сервера
vllm serve model --api-key "your-secret-key"

# У клієнті
client = VLLMSummarizerClient(
    api_key="your-secret-key"
)
```

### Обмеження доступу
```bash
# Тільки локальний доступ
vllm serve model --host 127.0.0.1

# З nginx reverse proxy
# Додай rate limiting, SSL, тощо
```

---

## 📚 Корисні посилання

- [vLLM Documentation](https://docs.vllm.ai/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Gemma Models](https://huggingface.co/google)

---

## 💡 Tips

✅ **Для розробки:** запускай сервер в окремому терміналі  
✅ **Для продакшену:** використовуй systemd або Docker  
✅ **Для швидкості:** увімкни prefix caching та chunked prefill  
✅ **Для економії пам'яті:** використовуй квантизацію (AWQ, GPTQ)  
✅ **Для масштабування:** додай tensor parallelism (`--tensor-parallel-size 2`)
