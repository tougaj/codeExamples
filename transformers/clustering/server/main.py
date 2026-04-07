"""
🚀 FastAPI сервер для кластеризації повідомлень
"""

import os
from contextlib import asynccontextmanager
from typing import Optional, cast

import hdbscan
import numpy as np
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from models import (ClusterInfo, ClusteringRequest, ClusteringResponse,
                    EmbeddingRequest, EmbeddingResponse, MessageId,
                    MessageIdWithSimilarity, SimilarityByIndex)
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

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


def get_similarity_by_index(embeddings: np.ndarray) -> list[SimilarityByIndex]:
    # 1️⃣ центроїд кластера 🧠
    # Що відбувається:
    # - Береться **середнє значення по всіх embedding'ах**
    # - `axis=0` → середнє по рядках (тобто по всіх текстах)
    # - `keepdims=True` → результат має форму `(1, embedding_dim)`, а не `(embedding_dim,)`
    # Інтуїція:
    # Центроїд — це **“середній зміст” усіх текстів**
    # 👉 Якщо уявити embeddings як точки в просторі:
    # - центроїд — це центр мас цього кластера
    centroid = embeddings.mean(axis=0, keepdims=True)

    # 2️⃣ cosine similarity до всіх текстів
    sims = cosine_similarity(centroid, embeddings)[0]

    # 3️⃣ індекси найближчих текстів (спадання)
    similarity_by_indexes = np.argsort(sims)[::-1]

    similarity: list[SimilarityByIndex] = []
    for index in similarity_by_indexes:
        similarity.append(SimilarityByIndex(index=index, similarity=sims[index]))

    return similarity


def get_clusters(ids: list[MessageId], embeddings: np.ndarray, min_cluster_size: int, min_samples: Optional[int]):
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,  # мін. розмір кластера
        min_samples=min_samples,           # чутливість до шуму

        # При низькій кількості повідомлень
        # min_cluster_size=3,      # мін. розмір кластера
        # min_samples=2,           # чутливість до шуму

        # Робочий варіант
        # min_cluster_size=7,      # мін. розмір кластера
        # min_samples=3,           # чутливість до шуму

        # Запропоновано GPT
        # min_cluster_size=5,      # мін. розмір кластера
        # min_samples=3,           # чутливість до шуму

        metric="euclidean",      # з нормалізованими векторами = cosine
        cluster_selection_method="eom"
        # cluster_selection_method="leaf"
    )
#     print(f"""ℹ️ Clustering parameters:
# - minimum cluster size: {min_cluster_size}
# - minimum samples count: {min_samples}""")

    labels = clusterer.fit_predict(embeddings)

    # групуємо тексти по кластерах 📦
    raw_clusters: dict[np.int64, list[MessageId]] = {}
    for msg_id, label in zip(ids, labels):
        raw_clusters.setdefault(label, []).append(msg_id)

    # сортуємо кластери за кількістю текстів (спадання ⬇️)
    sorted_clusters = sorted(
        raw_clusters.items(),
        key=lambda item: len(item[1]),
        reverse=True
    )

    result_clusters: list[ClusterInfo] = []
    for label, ids in sorted_clusters:
        if label == -1:
            continue
        embeds = embeddings[labels == label]

        # Формування заголовка на основі центроїда кластера (найближчий текст)
        similarity_by_indexes = get_similarity_by_index(embeddings=embeds)
        cluster_info = ClusterInfo(label=int(label), similarity=[])
        for sim in similarity_by_indexes:
            id = ids[sim.index]
            cluster_info.similarity.append(MessageIdWithSimilarity(id=id, similarity=sim.similarity))

        result_clusters.append(cluster_info)

    return result_clusters


@app.post("/clusters", response_model=ClusteringResponse)
def clustering(request: ClusteringRequest):
    """Кластеризація повідомлень"""
    embeddings: np.ndarray = np.array(request.embeddings, dtype=np.float32)
    clusters = get_clusters(request.ids, embeddings=embeddings, min_cluster_size=request.min_cluster_size, min_samples=request.min_samples)
    return clusters


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )
