import re
from typing import Optional

from pydantic import BaseModel, Field, computed_field, field_validator


class TextCleaner:
    """Клас для виконання очистки тексту від зайвих символів та мусору
    """
    re_emoji_pattern = re.compile(
        r'['
        r'\U0001F600-\U0001F64F'  # Emoticons
        r'\U0001F300-\U0001F5FF'  # Symbols & Pictographs
        r'\U0001F680-\U0001F6FF'  # Transport & Map Symbols
        r'\U0001F1E0-\U0001F1FF'  # Flags (iOS)
        r'\U00002600-\U000026FF'  # Miscellaneous Symbols
        r'\U00002700-\U000027BF'  # Dingbats
        r'\U0001F900-\U0001F9FF'  # Supplemental Symbols and Pictographs
        r'\U0001FA70-\U0001FAFF'  # Symbols & Pictographs Extended-A
        r'\U00002500-\U00002BEF'  # Chinese Symbols
        r']+|[\u2764\uFE0F\u200D]',  # ❤, модифікатори (FE0F, ZWJ)
        flags=re.UNICODE
    )
    re_pseudo_tag_pattern = re.compile(r'‹/?[a-z]+(?: [^›]*)?›')
    re_html_tag_pattern = re.compile(r'<\/?[a-z][^>]*>')
    re_url_pattern = re.compile(r'https?://\S+|www\.\S+')
    re_multiple_spaces = re.compile(r'[^\S\n]+')
    # re_multiple_spaces = re.compile(r'(?!\n)\s+') # Можна використовувати і такий RE

    def __init__(self, text: str):
        self.text = text

    def remove_unicode_symbols(self):
        """Видаляє з тексту символи unicode"""
        self.text = self.re_emoji_pattern.sub('', self.text)
        return self

    def remove_pseudo_tags(self):
        """Видаляє з тексту псевдотеги виду ‹b›"""
        self.text = self.re_pseudo_tag_pattern.sub('', self.text)
        return self

    def remove_html_tags(self):
        """Видаляє з тексту html теги"""
        self.text = self.re_html_tag_pattern.sub('', self.text)
        return self

    def remove_urls(self):
        """Видаляє з тексту URL-адреси"""
        self.text = self.re_url_pattern.sub('', self.text)
        return self

    def remove_multiple_spaces(self):
        """Видаляє з тексту зайві пробіли"""
        self.text = self.re_multiple_spaces.sub(' ', self.text)
        return self

    def remove_unnecessary_symbols(self):
        """Очищує текст від зайвого мусору"""
        return self.remove_urls().remove_unicode_symbols().remove_pseudo_tags().remove_html_tags().remove_multiple_spaces()

    def get_text(self):
        """Повертає очищений текст"""
        return self.text

    def get_stripped_text(self):
        """Повертає очищений текст"""
        return self.text.strip()


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

    @field_validator('title', 'body', mode='before')
    @classmethod
    def clean_text(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return TextCleaner(v).remove_unnecessary_symbols().get_stripped_text()

    @field_validator('summary',  'translated_title', 'translated_body',  mode='before')
    @classmethod
    def clean_summary(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return v.replace('**', '')

    @computed_field
    @property
    def text(self) -> str:
        # Текст на основі сумаризації
        title = (self.translated_title or self.title)[:200]
        exact_body = "\n".join((self.translated_body or self.body).split("\n")[:3])
        body = self.summary[:1000] if self.summary else exact_body
        return f"# {title}\n\n{body}"

        # Текст на основі тексту
        # title = remove_html_tags(self.translated_title or self.title)
        # body = remove_html_tags(self.translated_body or self.body)
        # # return f"{title[:100]}\n{body[:1000]}"
        # return f"{title[:100]}\n{"\n".join(body.split("\n")[:3])}"


# def remove_html_tags(text: str) -> str:
#     """
#     Видаляє всі HTML-теги з тексту, залишаючи лише вміст.

#     Args:
#         text (str): Вхідний рядок, що може містити HTML-теги.

#     Returns:
#         str: Текст без HTML-тегів.
#     """
#     clean = re.sub(r'<[^>]+>', '', text)
#     return clean


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
