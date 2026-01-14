import re
from typing import Optional

from pydantic import BaseModel, Field, computed_field, field_validator


class Message(BaseModel):
    url: str
    hit_date: str
    country: str
    title: str
    body: str
    language: Optional[str] = None
    summary: Optional[str] = None
    source_title: str
    translated_title: Optional[str] = None
    translated_body: Optional[str] = None

    @computed_field
    @property
    def text(self) -> str:
        # Текст на основі сумаризації
        title = remove_html_tags(self.translated_title or self.title)[:100]
        exact_body = "\n".join(remove_html_tags(self.translated_body or self.body).split("\n")[:3])
        body = self.summary.replace('**', '')[:1000] if self.summary else exact_body
        return f"{title}\n{body}"
        # return body

        # Текст на основі тексту
        # title = remove_html_tags(self.translated_title or self.title)
        # body = remove_html_tags(self.translated_body or self.body)
        # # return f"{title[:100]}\n{body[:1000]}"
        # return f"{title[:100]}\n{"\n".join(body.split("\n")[:3])}"


def remove_html_tags(text: str) -> str:
    """
    Видаляє всі HTML-теги з тексту, залишаючи лише вміст.

    Args:
        text (str): Вхідний рядок, що може містити HTML-теги.

    Returns:
        str: Текст без HTML-тегів.
    """
    clean = re.sub(r'<[^>]+>', '', text)
    return clean


class TopText(BaseModel):
    index: int
    similarity: float
    text: str


class TextCluster(BaseModel):
    label: int
    messages: list[Message]
    total_count: int
    texts: list[str]
    title: Optional[str] = None
    summary: Optional[str] = None


class SamplingParamsRequest(BaseModel):
    """Параметри генерації тексту"""

    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=512, ge=1, le=8192)
    presence_penalty: float = Field(default=0.5, ge=-2.0, le=2.0)
    frequency_penalty: float = Field(default=0.3, ge=-2.0, le=2.0)
    stop: Optional[list[str]] = Field(default=None)


class ChatRequest(BaseModel):
    """Запит для чат-генерації з промптом"""
    texts: list[str] = Field(..., min_length=1, max_length=200)
    prompt: str = Field(default="", description="Системний промпт для всіх текстів")
    sampling_params: Optional[SamplingParamsRequest] = None

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, v: list[str]) -> list[str]:
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

    results: list[GenerationResult]
    total_texts: int
    processing_time: float
    avg_input_tokens: Optional[float] = None
    avg_output_tokens: Optional[float] = None
    total_input_tokens: Optional[int] = None
    total_output_tokens: Optional[int] = None
