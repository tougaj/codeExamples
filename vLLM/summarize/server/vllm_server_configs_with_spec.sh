#!/bin/bash
# 📋 Різні конфігурації запуску vLLM сервера

# ============================================================================
# 🎯 Конфігурація 1: SPECULATIVE DECODING (рекомендовано для production)
# Gemma 12B + Gemma 4B draft
# Прискорення: ~1.5-2.5x, Якість: ідентична
# VRAM: ~32GB
# ============================================================================
start_speculative_decoding() {
    echo "🚀 Запуск з Speculative Decoding..."
    
    vllm serve google/gemma-2-12b-it \
        --host 0.0.0.0 \
        --port 8000 \
        --trust-remote-code \
        --max-model-len 8192 \
        --gpu-memory-utilization 0.85 \
        --speculative-model google/gemma-2-4b-it \
        --num-speculative-tokens 5 \
        --use-v2-block-manager \
        --enable-chunked-prefill \
        --enable-prefix-caching
}

# ============================================================================
# ⚡ Конфігурація 2: ТІЛЬКИ TARGET MODEL (без прискорення)
# Gemma 12B без draft
# Baseline для порівняння
# VRAM: ~24GB
# ============================================================================
start_baseline() {
    echo "🎯 Запуск baseline (без speculative decoding)..."
    
    vllm serve google/gemma-2-12b-it \
        --host 0.0.0.0 \
        --port 8000 \
        --trust-remote-code \
        --max-model-len 8192 \
        --gpu-memory-utilization 0.9 \
        --enable-prefix-caching
}

# ============================================================================
# 💨 Конфігурація 3: ТІЛЬКИ DRAFT MODEL (максимальна швидкість, менша якість)
# Gemma 4B
# Найшвидше, але можлива втрата якості
# VRAM: ~8GB
# ============================================================================
start_fast_only() {
    echo "💨 Запуск draft моделі (максимальна швидкість)..."
    
    vllm serve google/gemma-2-4b-it \
        --host 0.0.0.0 \
        --port 8000 \
        --trust-remote-code \
        --max-model-len 8192 \
        --gpu-memory-utilization 0.9 \
        --enable-prefix-caching
}

# ============================================================================
# 🔬 Конфігурація 4: NGRAM PROMPT LOOKUP (альтернатива spec decoding)
# Використовує n-gram lookup замість draft моделі
# Не потребує додаткової моделі, але менше прискорення
# VRAM: ~24GB
# ============================================================================
start_ngram_lookup() {
    echo "🔬 Запуск з N-gram Prompt Lookup..."
    
    vllm serve google/gemma-2-12b-it \
        --host 0.0.0.0 \
        --port 8000 \
        --trust-remote-code \
        --max-model-len 8192 \
        --gpu-memory-utilization 0.9 \
        --ngram-prompt-lookup-max 4 \
        --ngram-prompt-lookup-min 3 \
        --enable-prefix-caching
}

# ============================================================================
# 🎮 Конфігурація 5: MULTI-GPU з Speculative Decoding
# Tensor parallelism для дуже великих моделей
# Потребує 2+ GPU
# ============================================================================
start_multi_gpu_speculative() {
    echo "🎮 Запуск на multiple GPU..."
    
    vllm serve google/gemma-2-12b-it \
        --host 0.0.0.0 \
        --port 8000 \
        --trust-remote-code \
        --max-model-len 8192 \
        --tensor-parallel-size 2 \
        --gpu-memory-utilization 0.85 \
        --speculative-model google/gemma-2-4b-it \
        --num-speculative-tokens 5 \
        --use-v2-block-manager \
        --enable-chunked-prefill
}

# ============================================================================
# 🔐 Конфігурація 6: PRODUCTION з авторизацією
# З API key, rate limiting, logging
# ============================================================================
start_production() {
    echo "🔐 Запуск production конфігурації..."
    
    # Генеруй або задай свій API key
    API_KEY=${VLLM_API_KEY:-"your-secret-api-key-here"}
    
    vllm serve google/gemma-2-12b-it \
        --host 0.0.0.0 \
        --port 8000 \
        --trust-remote-code \
        --max-model-len 8192 \
        --gpu-memory-utilization 0.85 \
        --speculative-model google/gemma-2-4b-it \
        --num-speculative-tokens 5 \
        --use-v2-block-manager \
        --enable-chunked-prefill \
        --enable-prefix-caching \
        --api-key "$API_KEY" \
        --served-model-name gemma-12b-spec \
        --max-num-seqs 256 \
        --disable-log-requests false
}

# ============================================================================
# 🧪 Конфігурація 7: ЕКСПЕРИМЕНТАЛЬНА - різні num_speculative_tokens
# Для тестування оптимального значення
# ============================================================================
start_experimental() {
    NUM_SPEC_TOKENS=${1:-5}  # default 5, можна передати аргумент
    
    echo "🧪 Запуск з num_speculative_tokens=$NUM_SPEC_TOKENS..."
    
    vllm serve google/gemma-2-12b-it \
        --host 0.0.0.0 \
        --port 8000 \
        --trust-remote-code \
        --max-model-len 8192 \
        --gpu-memory-utilization 0.85 \
        --speculative-model google/gemma-2-4b-it \
        --num-speculative-tokens $NUM_SPEC_TOKENS \
        --use-v2-block-manager \
        --enable-chunked-prefill
}

# ============================================================================
# 🎯 ГОЛОВНЕ МЕНЮ
# ============================================================================
show_menu() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║          vLLM Server Configuration Selector                    ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Оберіть конфігурацію:"
    echo ""
    echo "  1) 🚀 Speculative Decoding (рекомендовано)"
    echo "     Gemma 12B + 4B draft, ~1.5-2.5x прискорення"
    echo ""
    echo "  2) 🎯 Baseline (без прискорення)"
    echo "     Тільки Gemma 12B, для порівняння"
    echo ""
    echo "  3) 💨 Fast Only (максимальна швидкість)"
    echo "     Тільки Gemma 4B"
    echo ""
    echo "  4) 🔬 N-gram Lookup"
    echo "     Альтернатива spec decoding без draft моделі"
    echo ""
    echo "  5) 🎮 Multi-GPU Speculative"
    echo "     Для систем з 2+ GPU"
    echo ""
    echo "  6) 🔐 Production"
    echo "     З API key та повним логуванням"
    echo ""
    echo "  7) 🧪 Experimental"
    echo "     Кастомні налаштування spec decoding"
    echo ""
    echo "  0) ❌ Вихід"
    echo ""
}

# ============================================================================
# MAIN
# ============================================================================
main() {
    while true; do
        show_menu
        read -p "Ваш вибір (0-7): " choice
        echo ""
        
        case $choice in
            1) start_speculative_decoding ;;
            2) start_baseline ;;
            3) start_fast_only ;;
            4) start_ngram_lookup ;;
            5) start_multi_gpu_speculative ;;
            6) start_production ;;
            7) 
                read -p "Введіть num_speculative_tokens (3-10, рекомендовано 5): " num_tokens
                start_experimental $num_tokens
                ;;
            0) 
                echo "👋 До побачення!"
                exit 0
                ;;
            *) 
                echo "❌ Невірний вибір. Спробуй ще раз."
                sleep 2
                ;;
        esac
    done
}

# Запуск меню
main
