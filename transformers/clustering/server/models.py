import numpy as np
from pydantic import BaseModel, Field, field_serializer, field_validator


class EmbeddingRequest(BaseModel):
    """Запит з текстами для обробки"""

    texts: list[str] = Field(..., min_length=1, max_length=10000)

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Список текстів не може бути порожнім")
        for text in v:
            if not text.strip():
                raise ValueError("Текст не може бути порожнім")
        return v


class EmbeddingResponse(BaseModel):
    embeddings: list[list[float]]


MessageId = str


class ClusteringRequestBase(BaseModel):
    ids: list[MessageId]
    embeddings: list[list[float]]  # нейтральний тип
    min_cluster_size: int
    min_samples: int


class ClusteringRequest(BaseModel):
    ids: list[str]
    # серверна версія — автоматично конвертує в ndarray
    embeddings: list[np.ndarray]
    min_cluster_size: int
    min_samples: int

    @field_validator("embeddings", mode="before")
    @classmethod
    def convert_embeddings(cls, v):
        # if not v:
        #     return v
        # # 🔥 якщо вже ndarray — нічого не робимо
        # if isinstance(v[0], np.ndarray):
        #     return v
        return [np.array(e) for e in v]

    # @field_serializer("embeddings")
    # def serialize_embeddings(self, v):
    #     return [e.tolist() for e in v]


class MessageIdWithSimilarity(BaseModel):
    id: MessageId
    similarity: float


class ClusterInfo(BaseModel):
    # Фактично це просто ідентифікатор кластеру
    label: int
    # Передбачається, що сортування відбувається по зменшенню схожості повідомлень з центроїдом
    similarity: list[MessageIdWithSimilarity]


ClusteringResponse = list[ClusterInfo]
