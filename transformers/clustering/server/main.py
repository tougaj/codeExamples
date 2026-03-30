"""
🚀 FastAPI сервер для роботи з vLLM моделями
Підтримує переклад, резюме та довільну генерацію тексту
"""

import os
import re
import time
from contextlib import asynccontextmanager
from typing import List, Optional, cast

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from health_checker import LLMHealthChecker
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from vllm.config.model import ModelDType
from vllm.model_executor.layers.quantization import QuantizationMethods

from interfaces import (BatchResponse, ChatRequest, GenerationResult,
                        HealthResponse, RawTextRequest, SamplingParamsRequest,
                        TextRequest)

# Завантаження змінних оточення
load_dotenv()

# 🔧 Глобальні змінні для моделі та токенайзера
llm: Optional[LLM] = None


# 🎬 Lifecycle управління
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ініціалізація та очищення ресурсів"""
    global llm, tokenizer, health_checker

    # Завантаження конфігурації з .env
    MODEL_NAME = os.getenv("MODEL_NAME", "google/gemma-3-4b-it")
    MAX_MODEL_LEN = int(os.getenv("MAX_MODEL_LEN", "8192"))
    GPU_MEMORY_UTILIZATION = float(os.getenv("GPU_MEMORY_UTILIZATION", "0.9"))
    QUANTIZATION = cast(QuantizationMethods, os.getenv("QUANTIZATION"))
    TENSOR_PARALLEL_SIZE = int(os.getenv("TENSOR_PARALLEL_SIZE", "1"))
    MAX_NUM_SEQS = int(os.getenv("MAX_NUM_SEQS", "15"))
    SWAP_SPACE = int(os.getenv("SWAP_SPACE", "8"))
    ENABLE_PREFIX_CACHING = os.getenv("ENABLE_PREFIX_CACHING", "true").lower() == "true"
    ENABLE_CHUNKED_PREFILL = (
        os.getenv("ENABLE_CHUNKED_PREFILL", "true").lower() == "true"
    )
    DTYPE = cast(ModelDType, os.getenv("DTYPE", "auto"))

    print("🔧 Ініціалізація vLLM моделі...")
    print(f"📦 Модель: {MODEL_NAME}")

    try:
        # Ініціалізація моделі
        llm = LLM(
            model=MODEL_NAME,
            max_model_len=MAX_MODEL_LEN,
            gpu_memory_utilization=GPU_MEMORY_UTILIZATION,
            tensor_parallel_size=TENSOR_PARALLEL_SIZE,
            max_num_seqs=MAX_NUM_SEQS,
            swap_space=SWAP_SPACE,
            enable_prefix_caching=ENABLE_PREFIX_CACHING,
            enable_chunked_prefill=ENABLE_CHUNKED_PREFILL,
            trust_remote_code=True,
            dtype=DTYPE,
            quantization=QUANTIZATION,
            # kv_cache_memory_bytes=1*1024*1024*1024
            # speculative_config={
            #     "model": "google/gemma-3-4b-it",
            #     "num_speculative_tokens": 128,
            #     "draft_tensor_parallel_size": 1,
            # },
        )

        # Ініціалізація токенайзера
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

        health_checker = LLMHealthChecker(llm=llm, ttl_seconds=60, verbose=True)

        print("✅ Модель успішно завантажена!")

    except Exception as e:
        print(f"❌ Помилка завантаження моделі: {e}")
        raise

    yield

    print("🔄 Вивантаження моделі...")


# 🚀 Ініціалізація FastAPI
app = FastAPI(
    title="vLLM API Server",
    description="API для роботи з vLLM моделями: переклад, резюме, генерація",
    version="1.0.0",
    lifespan=lifespan,
)


# 📍 Ендпоінти
@app.post("/summarize", response_model=BatchResponse)
async def summarize(request: TextRequest):
    """Створення резюме текстів українською мовою"""
    if llm is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Модель не завантажена",
        )

    # Підготовка промптів для резюме
    prompts = [prepare_summary_prompt(text, request.use_markdown) for text in request.texts]
    # print(prompts[0])

    # Параметри за замовчанням для резюме
    if request.sampling_params is None:
        request.sampling_params = SamplingParamsRequest(temperature=0.2, top_p=0.9, max_tokens=400)

    sampling_params = create_sampling_params(request.sampling_params)
    max_model_len = int(os.getenv("MAX_MODEL_LEN", "8192"))

    return await generate_texts(prompts, sampling_params, max_model_len)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )
    )
