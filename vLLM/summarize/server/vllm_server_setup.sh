#!/bin/bash
# 🚀 Скрипт для запуску vLLM OpenAI-compatible API сервера з Gemma 3

# Налаштування
MODEL_NAME="google/gemma-2-4b-it"
PORT=8000
HOST="0.0.0.0"  # 0.0.0.0 для доступу ззовні, 127.0.0.1 тільки локально
MAX_MODEL_LEN=8192
GPU_MEMORY_UTILIZATION=0.9

# 🎯 Запуск vLLM сервера
echo "🚀 Запуск vLLM OpenAI-compatible API сервера..."
echo "📦 Модель: $MODEL_NAME"
echo "🌐 Адреса: http://$HOST:$PORT"
echo ""

vllm serve $MODEL_NAME \
    --host $HOST \
    --port $PORT \
    --trust-remote-code \
    --max-model-len $MAX_MODEL_LEN \
    --gpu-memory-utilization $GPU_MEMORY_UTILIZATION \
    --tensor-parallel-size 1 \
    --dtype auto \
    --enable-prefix-caching \
    --disable-log-requests

# Додаткові корисні параметри (закоментовані):
# --api-key YOUR_SECRET_KEY \           # додати авторизацію
# --served-model-name gemma-3-4b \      # кастомна назва моделі в API
# --max-num-seqs 256 \                  # максимум одночасних sequences
# --enable-chunked-prefill \            # для довгих контекстів
# --quantization awq \                  # якщо використовуєш квантизовану модель

echo ""
echo "✅ Сервер запущено!"
echo "📚 API документація: http://$HOST:$PORT/docs"
echo "❤️  Health check: http://$HOST:$PORT/health"
echo ""
echo "🛑 Для зупинки натисни Ctrl+C"
