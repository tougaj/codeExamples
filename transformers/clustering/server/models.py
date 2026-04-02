from pydantic import BaseModel, Field, field_validator


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
