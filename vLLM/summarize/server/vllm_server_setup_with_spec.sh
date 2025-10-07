#!/bin/bash
# 🚀 Скрипт для запуску vLLM OpenAI-compatible API сервера з Speculative Decoding

# Налаштування моделей
TARGET_MODEL="google/gemma-2-12b-it"    # Основна модель (12B)
DRAFT_MODEL="google/gemma-2-4b-it"      # Draft модель (4B) для прискорення
PORT=8000
HOST="0.0.0.0"  # 0.0.0.0 для доступу ззовні, 127.0.0.1 тільки локально
MAX_MODEL_LEN=8192
GPU_MEMORY_UTILIZATION=0.85  # Трохи менше для двох моделей

# 🎯 Запуск vLLM сервера зі Speculative Decoding
echo "🚀 Запуск vLLM OpenAI-compatible API сервера..."
echo "🎯 Target Model: $TARGET_MODEL"
echo "⚡ Draft Model: $DRAFT_MODEL (speculative decoding)"
echo "🌐 Адреса: http://$HOST:$PORT"
echo ""

vllm serve $TARGET_MODEL \
    --host $HOST \
    --port $PORT \
    --trust-remote-code \
    --max-model-len $MAX_MODEL_LEN \
    --gpu-memory-utilization $GPU_MEMORY_UTILIZATION \
    --tensor-parallel-size 1 \
    --dtype auto \
    --enable-prefix-caching \
    --disable-log-requests \
    --speculative-model $DRAFT_MODEL \
    --num-speculative-tokens 5 \
    --use-v2-block-manager \
    --enable-chunked-prefill

# 💡 Параметри Speculative Decoding:
# --speculative-model: draft модель для генерації кандидатів
# --num-speculative-tokens: кількість токенів, які генерує draft (3-5 оптимально)
# --use-v2-block-manager: покращений memory manager для spec decoding
# --enable-chunked-prefill: ефективна робота з довгими контекстами

# Додаткові корисні параметри (закоментовані):
# --api-key YOUR_SECRET_KEY \           # додати авторизацію
# --served-model-name gemma-12b-spec \  # кастомна назва моделі в API
# --max-num-seqs 256 \                  # максимум одночасних sequences
# --ngram-prompt-lookup-max 4 \         # альтернатива: n-gram lookup замість draft моделі
# --speculative-max-model-len 8192 \    # max length для draft моделі

echo ""
echo "✅ Сервер запущено!"
echo "📚 API документація: http://$HOST:$PORT/docs"
echo "❤️  Health check: http://$HOST:$PORT/health"
echo ""
echo "🛑 Для зупинки натисни Ctrl+C"
