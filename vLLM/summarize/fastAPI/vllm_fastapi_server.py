"""
🚀 FastAPI сервер для роботи з vLLM моделями
Підтримує переклад, резюме та довільну генерацію тексту
"""

import os
import time
from contextlib import asynccontextmanager
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

# Завантаження змінних оточення
load_dotenv()

# 🔧 Глобальні змінні для моделі та токенайзера
llm: Optional[LLM] = None
tokenizer = None


# 📋 Pydantic моделі для запитів та відповідей
class SamplingParamsRequest(BaseModel):
    """Параметри генерації тексту"""

    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=512, ge=1, le=8192)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    stop: Optional[List[str]] = Field(default=None)


class TextRequest(BaseModel):
    """Запит з текстами для обробки"""

    texts: List[str] = Field(..., min_length=1, max_length=100)
    sampling_params: Optional[SamplingParamsRequest] = None

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Список текстів не може бути порожнім")
        for text in v:
            if not text.strip():
                raise ValueError("Текст не може бути порожнім")
        return v


class ChatRequest(BaseModel):
    """Запит для чат-генерації з промптом"""

    texts: List[str] = Field(..., min_length=1, max_length=100)
    sampling_params: Optional[SamplingParamsRequest] = None

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Список текстів не може бути порожнім")
        for text in v:
            if not text.strip():
                raise ValueError("Текст не може бути порожнім")
        return v


class RawTextRequest(BaseModel):
    """Запит для прямої генерації без chat template"""

    texts: List[str] = Field(..., min_length=1, max_length=100)
    sampling_params: Optional[SamplingParamsRequest] = None

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Список текстів не може бути порожнім")
        for text in v:
            if not text.strip():
                raise ValueError("Текст не може бути порожнім")
        return v


class GenerationResult(BaseModel):
    """Результат генерації для одного тексту"""

    text: str
    finish_reason: Optional[str]
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class BatchResponse(BaseModel):
    """Відповідь на batch запит"""

    results: List[GenerationResult]
    total_texts: int
    processing_time: float
    avg_input_tokens: Optional[float] = None
    avg_output_tokens: Optional[float] = None
    total_input_tokens: Optional[int] = None
    total_output_tokens: Optional[int] = None


class HealthResponse(BaseModel):
    """Відповідь health check"""

    status: str
    model_loaded: bool
    model_name: Optional[str] = None
    max_model_len: Optional[int] = None
    gpu_memory_utilization: Optional[float] = None


# 🎯 Функції для роботи з промптами
def prepare_translation_prompt(text: str) -> str:
    """Підготовка промпту для перекладу"""
    messages = [
        {
            "role": "user",
            "content": f"""Ти — професійний перекладач української мови.
Твоє завдання — перекласти отриманий текст українською **точно за змістом**, але **природно й виразно за формою**, дотримуючись таких правил:
1. Використовуй **граматично правильну, природну та стилістично доречну** українську мову.
2. **Не перекладай дослівно.** Уникай кальок, штучних зворотів і буквальних конструкцій — замінюй їх на природні українські відповідники або ідіоматичні вирази.
3. Використовуй українські лапки **«...»** замість іноземних варіантів („...", "...", '...' тощо), дотримуючись правил пунктуації.
4. За потреби застосовуй **форматування Markdown**:
   * заголовки (`#`, `##`),
   * списки,
   * **жирний** або *курсивний* текст,
   * **жирний** текст для іменованих сутностей (NER),
   * цитати тощо.
5. Не додавай пояснень, коментарів, приміток чи службових фраз.
6. Якщо надано текст українською, або російською мовою, то перекладати його не потрібно. В такому разі просто виведи пустий рядок.
7. **У відповіді подавай лише перекладений текст.**
Текст для перекладу:\n\n{text}""",
        }
    ]

    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )


def prepare_summary_prompt(text: str) -> str:
    """Підготовка промпту для резюме"""
    messages = [
        {
            "role": "user",
            "content": f"""Ти — система створення стислих новинних резюме.
Отримуєш текст статті з новинного джерела будь-якою мовою.
Твоє завдання — підготувати коротке резюме **українською мовою** (3–5 речень), дотримуючись таких правил:
1. Резюме має **обов'язково** бути українською мовою!.
2. **Передай головний зміст точно й стисло** — зосередься на ключових фактах, подіях і тезах.
3. Якщо в тексті є ці дані, **зазнач основних учасників, місце, час і причину події.**
4. **Уникай** другорядних деталей, прикладів, цитат, оцінних суджень і емоційного тону.
5. Дотримуйся **нейтрального, об'єктивного та інформативного стилю.**
6. Використовуй **природну, зрозумілу й граматично правильну** українську мову.
7. Використовуй Markdown **жирний** текст для іменованих сутностей (NER).
8. **У відповіді подай лише резюме** — без коментарів, пояснень, заголовків або форматування.
Текст для резюме:\n\n{text}""",
        }
    ]

    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )


def prepare_chat_prompt(text: str) -> str:
    """Підготовка промпту для довільної генерації"""
    messages = [
        {
            "role": "user",
            "content": text,
        }
    ]

    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )


def validate_text_length(text: str, max_model_len: int) -> None:
    """Валідація довжини тексту"""
    # Приблизна оцінка: 1 токен ≈ 4 символи
    estimated_tokens = len(text) / 4

    if estimated_tokens > max_model_len * 0.8:  # залишаємо 20% для відповіді
        raise ValueError(
            f"Текст занадто довгий. Приблизна кількість токенів: {int(estimated_tokens)}, "
            f"максимально допустимо: {int(max_model_len * 0.8)}"
        )


def create_sampling_params(params: Optional[SamplingParamsRequest]) -> SamplingParams:
    """Створення SamplingParams з опціональних параметрів"""
    if params is None:
        params = SamplingParamsRequest()

    return SamplingParams(
        temperature=params.temperature,
        top_p=params.top_p,
        max_tokens=params.max_tokens,
        presence_penalty=params.presence_penalty,
        frequency_penalty=params.frequency_penalty,
        stop=params.stop,
    )


async def generate_texts(
    texts: List[str], sampling_params: SamplingParams, max_model_len: int
) -> BatchResponse:
    """Генерація текстів через vLLM"""
    start_time = time.time()

    try:
        # Валідація довжини кожного тексту
        for i, text in enumerate(texts):
            try:
                validate_text_length(text, max_model_len)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Помилка валідації тексту #{i + 1}: {str(e)}",
                )

        # Генерація
        outputs = llm.generate(texts, sampling_params)

        # Обробка результатів
        results = []
        total_input_tokens = 0
        total_output_tokens = 0

        for output in outputs:
            # Отримання токенів з метрик
            prompt_tokens = len(output.prompt_token_ids) if output.prompt_token_ids else None
            completion_tokens = (
                len(output.outputs[0].token_ids) if output.outputs[0].token_ids else None
            )

            if prompt_tokens is not None:
                total_input_tokens += prompt_tokens
            if completion_tokens is not None:
                total_output_tokens += completion_tokens

            results.append(
                GenerationResult(
                    text=output.outputs[0].text.strip(),
                    finish_reason=output.outputs[0].finish_reason,
                    input_tokens=prompt_tokens,
                    output_tokens=completion_tokens,
                )
            )

        processing_time = time.time() - start_time

        # Розрахунок середніх значень
        valid_input_tokens = [r.input_tokens for r in results if r.input_tokens is not None]
        valid_output_tokens = [
            r.output_tokens for r in results if r.output_tokens is not None
        ]

        return BatchResponse(
            results=results,
            total_texts=len(texts),
            processing_time=round(processing_time, 4),
            avg_input_tokens=(
                round(sum(valid_input_tokens) / len(valid_input_tokens), 2)
                if valid_input_tokens
                else None
            ),
            avg_output_tokens=(
                round(sum(valid_output_tokens) / len(valid_output_tokens), 2)
                if valid_output_tokens
                else None
            ),
            total_input_tokens=total_input_tokens if total_input_tokens > 0 else None,
            total_output_tokens=total_output_tokens if total_output_tokens > 0 else None,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при генерації: {str(e)}",
        )


# 🎬 Lifecycle управління
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ініціалізація та очищення ресурсів"""
    global llm, tokenizer

    # Завантаження конфігурації з .env
    MODEL_NAME = os.getenv("MODEL_NAME", "google/gemma-3-4b-it")
    MAX_MODEL_LEN = int(os.getenv("MAX_MODEL_LEN", "8192"))
    GPU_MEMORY_UTILIZATION = float(os.getenv("GPU_MEMORY_UTILIZATION", "0.9"))
    TENSOR_PARALLEL_SIZE = int(os.getenv("TENSOR_PARALLEL_SIZE", "1"))
    MAX_NUM_SEQS = int(os.getenv("MAX_NUM_SEQS", "15"))
    SWAP_SPACE = int(os.getenv("SWAP_SPACE", "8"))
    ENABLE_PREFIX_CACHING = os.getenv("ENABLE_PREFIX_CACHING", "true").lower() == "true"
    ENABLE_CHUNKED_PREFILL = (
        os.getenv("ENABLE_CHUNKED_PREFILL", "true").lower() == "true"
    )
    DTYPE = os.getenv("DTYPE", "auto")

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
            dtype=DTYPE,
        )

        # Ініціалізація токенайзера
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

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
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Перевірка стану сервера"""
    if llm is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "model_loaded": False},
        )

    return HealthResponse(
        status="healthy",
        model_loaded=True,
        model_name=os.getenv("MODEL_NAME", "google/gemma-3-4b-it"),
        max_model_len=int(os.getenv("MAX_MODEL_LEN", "8192")),
        gpu_memory_utilization=float(os.getenv("GPU_MEMORY_UTILIZATION", "0.9")),
    )


@app.post("/translate", response_model=BatchResponse)
async def translate(request: TextRequest):
    """Переклад текстів українською мовою"""
    if llm is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Модель не завантажена",
        )

    # Підготовка промптів для перекладу
    prompts = [prepare_translation_prompt(text) for text in request.texts]

    # Параметри за замовчанням для перекладу
    if request.sampling_params is None:
        request.sampling_params = SamplingParamsRequest(
            temperature=0.1, top_p=0.9, max_tokens=8192
        )

    sampling_params = create_sampling_params(request.sampling_params)
    max_model_len = int(os.getenv("MAX_MODEL_LEN", "8192"))

    return await generate_texts(prompts, sampling_params, max_model_len)


@app.post("/summarize", response_model=BatchResponse)
async def summarize(request: TextRequest):
    """Створення резюме текстів українською мовою"""
    if llm is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Модель не завантажена",
        )

    # Підготовка промптів для резюме
    prompts = [prepare_summary_prompt(text) for text in request.texts]

    # Параметри за замовчанням для резюме
    if request.sampling_params is None:
        request.sampling_params = SamplingParamsRequest(
            temperature=0.5,
            top_p=0.9,
            max_tokens=400,
            presence_penalty=0.5,
            frequency_penalty=0.3,
        )

    sampling_params = create_sampling_params(request.sampling_params)
    max_model_len = int(os.getenv("MAX_MODEL_LEN", "8192"))

    return await generate_texts(prompts, sampling_params, max_model_len)


@app.post("/generate", response_model=BatchResponse)
async def generate(request: ChatRequest):
    """Довільна генерація з використанням chat template"""
    if llm is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Модель не завантажена",
        )

    # Підготовка промптів через chat template
    prompts = [prepare_chat_prompt(text) for text in request.texts]

    sampling_params = create_sampling_params(request.sampling_params)
    max_model_len = int(os.getenv("MAX_MODEL_LEN", "8192"))

    return await generate_texts(prompts, sampling_params, max_model_len)


@app.post("/generate-raw", response_model=BatchResponse)
async def generate_raw(request: RawTextRequest):
    """Пряма генерація без chat template (сирий текст)"""
    if llm is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Модель не завантажена",
        )

    # Використання текстів напряму, без chat template
    prompts = request.texts

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
