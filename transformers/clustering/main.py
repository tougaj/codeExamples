from sentence_transformers import SentenceTransformer
from pprint import pprint
import hdbscan
from collections import Counter

def main():
    texts = [
        "На Дніпропетровщині та Запоріжжі частково відновлюють світло: яка зараз ситуація в регіонах",
        "“Надзвичайна ситуація національного рівня”: мер Дніпра Філатов розповів про стан справ в місті після блекауту",
        "Російські атаки залишили без світла Запорізьку та Дніпропетровську області ",
        "Запоріжжя знову зі світлом після масштабного блекауту. У Дніпрі електроенергії поки немає, ситуація складна",
        "На Дніпропетровщині без струму залишились 8 вугільних шахт (Відео)",
        "Трамп підтримав законопроект про санкції проти Росії",
        "Сенатор Грэм: Трамп одобрил законопроект о новых санкциях на российскую нефть",
        "В Україні відреагували на \"зелене світло\" від Трампа на санкції США проти Росії",
        "Трамп дав «зелене світло» санкційному законопроєкту проти росії — Ґрем",
        "Трамп дозволив Конгресу просунути санкційний законопроєкт проти партнерів Росії",
        "Шуфричу дозволили вийти з СІЗО під заставу",
        "Велика Британія передала Україні 13 систем ППО Raven і розпочала постачання Gravehawk",
        "Менше, ніж очікували: скільки своїх солдатів країни Заходу готові направити в Україну",
        "Шуфричу дозволили вийти з-під варти під заставу у понад 33 млн грн",
        "Суд випустив Шуфрича з-під варти",

    ]

    model = SentenceTransformer(
        # "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        # "sentence-transformers/all-MiniLM-L6-v2"
        "google/embeddinggemma-300m"
    )

    print("ℹ️ Calculating embeddings...")
    embeddings = model.encode(
        texts,
        batch_size=16,
        show_progress_bar=True,
        normalize_embeddings=True  # ВАЖЛИВО для HDBSCAN
    )
    
    # for e in embeddings:
    #     pprint(e)

    print("ℹ️ Clustering...")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=3,      # мін. розмір кластера
        min_samples=2,           # чутливість до шуму
        # min_cluster_size=5,      # мін. розмір кластера
        # min_samples=3,           # чутливість до шуму
        metric="euclidean",      # з нормалізованими векторами = cosine
        cluster_selection_method="eom"
    )

    labels = clusterer.fit_predict(embeddings)
    pprint(Counter(labels))

    clusters = {}
    for text, label in zip(texts, labels):
        clusters.setdefault(label, []).append(text)

    for label, items in clusters.items():
        print(f"\nCLUSTER {label} ({len(items)})")
        pprint(items)
        # print(items[0][:300])


if __name__ == "__main__":
    main()
