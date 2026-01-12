from collections import Counter
from pprint import pprint

import hdbscan
import numpy as np
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from data import load_json_file
from interfaces import BatchResponse, ChatRequest, Message, TopText

SERVER_ADDRESS = "http://127.0.0.1:9001"
REQUEST_TIMEOUT = 300
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


def get_cluster_title(messages: list[Message]):
    texts_for_process = [msg.text for msg in messages]
    texts = "\n---\n".join(texts_for_process)
    prompt = """Тобі надано набір текстів, розділених рядком \n---\n.
Усі тексти належать до однієї спільної тематики та є змістовно пов’язаними (кластер схожих статей).
Твоє завдання — визначити спільну тему цих текстів і сформулювати розгорнуту, чітку та зрозумілу назву, якою можна їх озаглавити.

Вимоги до назви:
- українською мовою
- повне речення або складний іменниковий заголовок
- чітко відображає суть усіх текстів
- без лапок
- без пояснень, коментарів чи списків
- без абстрактних слів типу «Різне», «Інше», «Огляд теми»

Поверни лише назву тематики одним рядком.

Набір текстів:"""
#     prompt = """Завдання:
# Дай розгорнуту назву теми для наступного набору текстів, розділених за допомогою '---'.
# Відповідь надай українською мовою.
# Тексти для визначення теми:

# """
    request_data: ChatRequest = ChatRequest(texts=[texts], prompt=prompt)
    print(f"🧐 Generating titles")

    response = requests.post(f"{SERVER_ADDRESS}/generate", json=request_data.model_dump(), timeout=REQUEST_TIMEOUT)
    raw_data = response.json()
    if response.status_code == 200:
        model_answer = BatchResponse.model_validate(raw_data)
        print(model_answer.results[0].text)
        # results = []
        # for msg, estimation in zip(messages, model_answer.results):
        #     results.append({"estimation": estimation.text, "msg": msg.text})
        # print(results)


def get_cluster_summary(messages: list[Message]):
    texts_for_process = [msg.text for msg in messages]
    texts = "\n---\n".join(texts_for_process)
    prompt = """Ти — система створення новинних резюме.

Отримуєш набір текстів, розділених рядком \n---\n.

Усі тексти належать до однієї спільної тематики та є змістовно пов’язаними (кластер схожих статей).

Твоє завдання — підготувати резюме **українською мовою**, дотримуючись таких правил:

- Резюме має **обов'язково** бути українською мовою!.
- **Передай головний зміст точно й стисло** — зосередься на ключових фактах, подіях і тезах.
- Якщо в тексті є **основні учасники, місце, час, причина події**, зазнач це.
- **Уникай** другорядних деталей, прикладів, цитат, оцінних суджень і емоційного тону.
- Дотримуйся **нейтрального, об'єктивного та інформативного стилю.**
- Використовуй **природну, зрозумілу й граматично правильну** українську мову.
- Довжина резюме має бути від 2 до 3 абзаців, кожен з яких містить від 3 до 5 бажано простих речень.
- **У відповіді подай лише резюме** — без коментарів, пояснень, заголовків.
- **Заборонено додавати інформацію, якої немає в оригіналі**, навіть якщо вона здається очевидною або логічною за контекстом.
- **Не роби припущень** щодо осіб, подій, дат, країн, географічних назв чи фактів. Якщо в тексті не вказано ім’я чи назва суб'єкту — не вигадуй його.
- **Не додавай** жодних імен, ролей, подій чи фактів, яких **немає в оригіналі**. Якщо в оригіналі немає конкретної назви або імені — **не вигадуй їх**, навіть якщо це звучить природніше.
- **Заборонено** додавати вигадані імена, факти, уточнення, дати, країни, географічні назви, інтерпретації чи пояснення.
- **Не інтерпретуй** і не додавай причин, мотивів чи додаткових деталей, яких немає в тексті.
- Якщо в оригіналі іменовані сутності іншою мовою — **переклади їх українською**.
- **Заборонено припускати**, що в тексті йдеться про Україну, якщо тільки це не вказано явно в оригіналі.
- Враховуй те, що 24 лютого 2022 року Росія агресивно напала на Україну з метою знищення української державності і наразі ці дві країни знаходяться в стані війни.
- Використовуй Markdown **жирний** текст для виділення іменованих сутностей (NER).

Набір текстів:"""

    request_data: ChatRequest = ChatRequest(texts=[texts], prompt=prompt)
    print(f"🧐 Generating summaries")

    response = requests.post(f"{SERVER_ADDRESS}/generate", json=request_data.model_dump(), timeout=REQUEST_TIMEOUT)
    raw_data = response.json()
    if response.status_code == 200:
        model_answer = BatchResponse.model_validate(raw_data)
        print(model_answer.results[0].text)


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
    for index, (label, messages) in enumerate(sorted_clusters, start=1):
        if label == -1:
            continue
        # Формування заголовка на основі центроїда кластера (найближчий текст)
        texts_cluster = [item.text for item in messages]
        embeds_cluster = embeddings[[i for i, l in enumerate(labels) if l == label]]

        # Формування заголовка на основі центроїда кластера (найближчий текст)
        centroid, title_text, top_texts = cluster_centroid_and_top_texts(texts_cluster, embeds_cluster)
        top_messages = [messages[text.index] for text in top_texts]
        cluster_title = get_cluster_title(top_messages)
        cluster_summary = get_cluster_summary(top_messages)

        print(f"\n📦 CLUSTER {index} of {labels_count} (label: {label}) ({len(messages)} messages)")
        # top_item = items[index]
        print_centroid_message_info(messages, top_texts[0].index)
        # print(f"📰 {title_text}")
        # pprint(top_texts)
        # pprint([f"📐 {item["similarity"]*100:.1f} % {item["text"]}" for item in top_texts])
        for text in top_texts:
            print(f"📐 {text.similarity*100:.1f}% {text.text}")

    pprint(Counter(labels))


if __name__ == "__main__":
    main()
