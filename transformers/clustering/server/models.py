from typing import Optional

from pydantic import BaseModel, Field, field_validator


# embeddings
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

# EmbeddingResponse = list[list[float]]


# clustering
MessageId = str


class ClusteringRequest(BaseModel):
    ids: list[str]
    embeddings: list[list[float]]
    min_cluster_size: int
    min_samples: Optional[int]
    ignore_empty_cluster: bool = True

# Це цікавий кейс з використання валідаторів та серіалізаторів.
# Нажаль, в цьому проекті він не працює, але я залишу це для прикладу.
# class ClusteringRequest(BaseModel):
#     ids: list[str]
#     # серверна версія — автоматично конвертує в ndarray
#     embeddings: list[np.ndarray]
#     min_cluster_size: int
#     min_samples: int

#     @field_validator("embeddings", mode="before")
#     @classmethod
#     def convert_embeddings(cls, v):
#         if not v:
#             return v
#         # 🔥 якщо вже ndarray — нічого не робимо
#         if isinstance(v[0], np.ndarray):
#             return v
#         return [np.array(e) for e in v]

#     @field_serializer("embeddings")
#     def serialize_embeddings(self, v):
#         return [e.tolist() for e in v]

# Clustering


class SimilarityByIndex(BaseModel):
    index: int
    similarity: float


class MessageIdWithSimilarity(BaseModel):
    id: MessageId
    similarity: float


# class ClusterInfoWithTexts(BaseModel):
#     # Фактично це просто ідентифікатор кластеру
#     label: int
#     # Передбачається, що сортування id відбувається по зменшенню схожості повідомлень з центроїдом
#     ids: list[MessageId]
#     messages: dict[MessageId, ProcessedMessage]
#     title: Optional[str] = None
#     summary: Optional[str] = None


class ClusterInfo(BaseModel):
    # Фактично це просто ідентифікатор кластеру
    label: int
    # Передбачається, що сортування відбувається по зменшенню схожості повідомлень з центроїдом
    similarity: list[MessageIdWithSimilarity]


ClusteringResponse = list[ClusterInfo]
