import re
from typing import Optional

from pydantic import BaseModel, computed_field


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
        return remove_html_tags(self.summary or self.translated_body or self.body)


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
