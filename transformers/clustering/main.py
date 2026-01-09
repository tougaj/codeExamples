from sentence_transformers import SentenceTransformer
from pprint import pprint
import hdbscan
from collections import Counter
from data import _texts

def main():

    texts = [text[:1000] for text in _texts]

    model = SentenceTransformer(
        # "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        # "sentence-transformers/all-MiniLM-L6-v2"
        "google/embeddinggemma-300m"
        # "Qwen/Qwen3-Embedding-0.6B"
        # "Qwen/Qwen3-Embedding-8B"
    )

    print("ℹ️ Calculating embeddings...")
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True  # ВАЖЛИВО для HDBSCAN
    )
    
    # for e in embeddings:
    #     pprint(e)

    print("ℹ️ Clustering...")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=3,      # мін. розмір кластера
        min_samples=2,           # чутливість до шуму

        # min_cluster_size=7,      # мін. розмір кластера
        # min_samples=3,           # чутливість до шуму

        # min_cluster_size=5,      # мін. розмір кластера
        # min_samples=3,           # чутливість до шуму
        metric="euclidean",      # з нормалізованими векторами = cosine
        cluster_selection_method="eom"
    )

    labels = clusterer.fit_predict(embeddings)

    # групуємо тексти по кластерах 📦
    clusters = {}
    for text, label in zip(texts, labels):
        clusters.setdefault(label, []).append(text)

    # сортуємо кластери за кількістю текстів (спадання ⬇️)
    sorted_clusters = sorted(
        clusters.items(),
        key=lambda item: len(item[1]),
        reverse=True
    )

    # виводимо результат 🖨️
    for index, (label, items) in enumerate(sorted_clusters, 1):
        if label == -1:
                continue
        print(f"\nCLUSTER {index} (label {label}) ({len(items)})")
        pprint([item[:200] for item in items[:10]])
        # print(f"\nCLUSTER {label} ({len(items)})")
        # print(items[0][:300])

    # clusters = {}
    # for text, label in zip(texts, labels):
    #     clusters.setdefault(label, []).append(text)

    # for label, items in clusters.items():
    #     if label == -1:
    #         continue
    #     print(f"\nCLUSTER {label} ({len(items)})")
    #     pprint([item[:200] for item in items])
    #     # print(items[0][:300])

    pprint(Counter(labels))


if __name__ == "__main__":
    main()
