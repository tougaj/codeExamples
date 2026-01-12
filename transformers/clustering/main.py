import re
from collections import Counter
from pprint import pprint

import hdbscan
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from data import load_json_file
from interfaces import Message, TopText

# def cluster_title_centroid(texts, embeddings):
#     centroid = embeddings.mean(axis=0, keepdims=True)
#     sims = cosine_similarity(centroid, embeddings)[0]
#     best_idx = sims.argmax()
#     # return texts[best_idx][:200]  # обрізаємо
#     return texts[best_idx]


def cluster_centroid_and_top_texts(texts: list[str], embeddings, top_k=10, preview_len=10000):
    """
    Повертає:
    - centroid (np.array)
    - representative_text (str)
    - top_texts: список dict {text, similarity, index}
    """

    # 1️⃣ центроїд кластера 🧠
    centroid = embeddings.mean(axis=0, keepdims=True)

    # 2️⃣ cosine similarity до всіх текстів
    sims = cosine_similarity(centroid, embeddings)[0]

    # 3️⃣ індекси top-k найближчих текстів (спадання)
    top_indices = np.argsort(sims)[::-1][:top_k]

    top_texts = [
        TopText(index=int(i), similarity=float(sims[i]), text=texts[i][:preview_len])
        for i in top_indices
    ]

    representative_text = top_texts[0].text

    return centroid[0], representative_text, top_texts


def print_centroid_message_info(messages: list[Message], index: int):
    message = messages[index]
    print(f"🖊️ {message.title}")
    # print(f"📰 {message["text"]}")


def main():
    messages = load_json_file("local.data.json")
    # for text in data:
    #     text["text"] = get_text(text)
    # texts = [get_text(item) for item in data]
    # texts = [remove_html_tags(text)[:1000] for text in messages]

    model = SentenceTransformer(
        # "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        # "sentence-transformers/all-MiniLM-L6-v2"
        "google/embeddinggemma-300m"
        # "Qwen/Qwen3-Embedding-0.6B"
        # "Qwen/Qwen3-Embedding-8B"
    )

    print("ℹ️ Calculating embeddings...")
    embeddings = model.encode(
        [msg.text for msg in messages],
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True  # ВАЖЛИВО для HDBSCAN
    )

    # for e in embeddings:
    #     pprint(e)

    print("ℹ️ Clustering...")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=7,      # мін. розмір кластера
        min_samples=3,           # чутливість до шуму

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
    )

    labels = clusterer.fit_predict(embeddings)

    # групуємо тексти по кластерах 📦
    clusters: dict[np.int64, list[Message]] = {}
    for text, label in zip(messages, labels):
        clusters.setdefault(label, []).append(text)

    # сортуємо кластери за кількістю текстів (спадання ⬇️)
    sorted_clusters = sorted(
        clusters.items(),
        key=lambda item: len(item[1]),
        reverse=True
    )

    # виводимо результат 🖨️
    labels_count = len(sorted_clusters)
    for index, (label, items) in enumerate(sorted_clusters, start=1):
        # Формування заголовка на основі центроїда кластера (найближчий текст)
        texts_cluster = [item.text for item in items]
        embeds_cluster = embeddings[[i for i, l in enumerate(labels) if l == label]]

        # Формування заголовка на основі центроїда кластера (найближчий текст)
        centroid, title_text, top_texts = cluster_centroid_and_top_texts(texts_cluster, embeds_cluster)

        print(f"\n📦 CLUSTER {index} of {labels_count} (label: {label}) ({len(items)} messages)")
        # top_item = items[index]
        print_centroid_message_info(items, top_texts[0].index)
        # print(f"📰 {title_text}")
        # pprint(top_texts)
        # pprint([f"📐 {item["similarity"]*100:.1f} % {item["text"]}" for item in top_texts])
        for text in top_texts:
            print(f"📐 {text.similarity*100:.1f}% {text.text}")

    pprint(Counter(labels))


if __name__ == "__main__":
    main()
