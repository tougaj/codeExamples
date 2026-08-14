# extract.py
# /// script
# dependencies = ["trafilatura"]
# ///

import sys
import trafilatura

def extract_article(url: str) -> str | None:
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        print(f"⚠️ Не вдалося завантажити: {url}", file=sys.stderr)
        return None

    text = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=False,
        favor_precision=True,   # менше "сміття", ризик втратити трохи тексту
        deduplicate=True,
        output_format="json",
        with_metadata=True
    )
    return text


if __name__ == "__main__":
    url = sys.argv[1]
    article_text = extract_article(url)

    if article_text:
        print(article_text)
    else:
        print("Текст не знайдено або сторінка порожня.", file=sys.stderr)
        sys.exit(1)