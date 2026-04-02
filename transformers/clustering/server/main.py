"""
🚀 FastAPI сервер для кластеризації повідомлень
"""

import os
from contextlib import asynccontextmanager
from typing import cast

import numpy as np
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from models import EmbeddingRequest, EmbeddingResponse
from sentence_transformers import SentenceTransformer

# Завантаження змінних оточення
load_dotenv()


# state
class AppState:
    model: SentenceTransformer
    batch_size: int


def get_state(request: Request) -> AppState:
    return cast(AppState, request.app.state)


def get_model(state: AppState = Depends(get_state)) -> SentenceTransformer:
    if state.model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Модель не завантажена",
        )
    return state.model


def get_batch_size(state: AppState = Depends(get_state)) -> int:
    return state.batch_size


# 🎬 Lifecycle управління
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ініціалізація та очищення ресурсів"""
    # Завантаження конфігурації з .env
    MODEL_NAME = os.getenv("MODEL_NAME", "google/embeddinggemma-300m")

    print("🔧 Ініціалізація embedding-моделі...")
    print(f"📦 Модель: {MODEL_NAME}")

    try:
        # Завантажити локальну модель можна так (тут вказується каталог, де знаходиться config.json):
        # model = SentenceTransformer("/data/hf_home/hub/models--google--embeddinggemma-300m/snapshots/57c266a740f537b4dc058e1b0cda161fd15afa75")

        # Ініціалізація моделі
        model = SentenceTransformer(
            MODEL_NAME
            # , local_files_only=True # ⚠️ For using local model
        )
        app.state.model = model
        batch_size = int(os.getenv("BATCH_SIZE", "32"))
        app.state.batch_size = batch_size
        print(f"""✅ Параметри успішно завантажені!
- модель: {MODEL_NAME}
- batch size: {batch_size}""")
    except Exception as e:
        print(f"❌ Помилка завантаження моделі: {e}")
        raise

    yield

    print("🔄 Вивантаження моделі...")


# 🚀 Ініціалізація FastAPI
app = FastAPI(
    title="Clustering API Server",
    description="API для кластеризації повідомлень",
    version="1.0.0",
    lifespan=lifespan,
)


def get_embeddings(texts: list[str], model: SentenceTransformer, batch_size: int) -> np.ndarray:
    return model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True  # ВАЖЛИВО для HDBSCAN
    )


# 📍 Ендпоінти
@app.post("/embed", response_model=EmbeddingResponse)
def embed(request: EmbeddingRequest, model: SentenceTransformer = Depends(get_model), batch_size: int = Depends(get_batch_size)):
    """Генерація embeddings для переданих текстів"""
    embeddings: np.ndarray = get_embeddings(request.texts, model=model, batch_size=batch_size)
    return {
        "embeddings": embeddings.tolist(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )
