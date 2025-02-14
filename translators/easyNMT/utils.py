"""
Утиліти, що використовуються в процесі визначення мови тексту, або його перекладу.
Оригінальний файл знаходиться за адресою:
https://github.com/tougaj/portal/blob/main/utils/news_language/utils.py
"""
import re

from langdetect import DetectorFactory, detect

BODY_MIN_LENGTH = 100

# From https://pypi.org/project/langdetect/
# Language detection algorithm is non-deterministic, which means that if you try to run it on a text which is either too short or too ambiguous, you might get different results everytime you run it.
# To enforce consistent results, call following code before the first language detection:
DetectorFactory.seed = 0


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


def detect_language(text: str, min_length=BODY_MIN_LENGTH, verbose=True):
    """Функція для визначення мови тексту.
    Попередньо проводиться очищення тексту від зайвого форматування та мусора"""
    empty_result = (None, None)
    cleaned_text = TextCleaner(text).remove_unnecessary_symbols().get_stripped_text()
    if len(cleaned_text) < min_length:
        if verbose:
            print(f"⚠️ Text is too small ({len(cleaned_text)} characters, min_length={min_length})")
        return empty_result
    try:
        lang = detect(cleaned_text)
    except Exception as e:
        if verbose:
            print(f"⚠️ Error: {e}")
    return (lang, cleaned_text) if lang else empty_result
