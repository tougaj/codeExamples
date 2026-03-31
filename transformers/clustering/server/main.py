"""
🚀 FastAPI сервер для кластеризації повідомлень
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
# from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer

from interfaces import EmbeddingResponse, TextRequest

# Завантаження змінних оточення
load_dotenv()


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
        print("✅ Модель успішно завантажена!")
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


def get_model(request: Request) -> SentenceTransformer:
    return request.app.state.model

# 📍 Ендпоінти


@app.post("/embed", response_model=EmbeddingResponse)
def embed(request: TextRequest, model: SentenceTransformer = Depends(get_model)):
    """Створення резюме текстів українською мовою"""
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Модель не завантажена",
        )

    embeddings: np.ndarray = model.encode(
        request.texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True  # ВАЖЛИВО для HDBSCAN
    )
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
