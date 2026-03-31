import os
import sys
from collections import Counter
from pprint import pprint

import hdbscan
import numpy as np
import requests
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

from data import load_json_file
from interfaces import (BatchResponse, ChatRequest, Message,
                        SamplingParamsRequest, TextCluster, TopText)
from server.interfaces import EmbeddingRequest, EmbeddingResponse

load_dotenv()

EMBEDDING_SERVER_ADDRESS = os.getenv("EMBEDDING_SERVER", "http://127.0.0.1:8000")
LLM_SERVER_ADDRESS = os.getenv("LLM_SERVER", "http://127.0.0.1:8000")
REQUEST_TIMEOUT = int(os.getenv("REQUESTS_TIMEOUT", "300"))

# def cluster_title_centroid(texts, embeddings):
#     centroid = embeddings.mean(axis=0, keepdims=True)
#     sims = cosine_similarity(centroid, embeddings)[0]
#     best_idx = sims.argmax()
#     # return texts[best_idx][:200]  # обрізаємо
#     return texts[best_idx]


def cluster_centroid_and_top_texts(embeddings, top_k=10):
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
        TopText(index=int(i), similarity=float(sims[i]))
        for i in top_indices
    ]

    return centroid[0], top_texts


def print_centroid_message_info(messages: list[Message], index: int):
    message = messages[index]
    print(f"🖊️ {message.title}")
    # print(f"📰 {message["text"]}")


def get_cluster_title(texts: list[str]):
    prompt = """Тобі надано набір текстів, розділених рядком \n---\n.
Усі тексти належать до однієї спільної тематики та є змістовно пов’язаними (кластер схожих статей).
Твоє завдання — визначити спільну тему цих текстів і сформулювати розгорнуту, чітку та зрозумілу назву, якою можна їх озаглавити.

### Вимоги до назви:

- українською мовою
- повне речення або складний іменниковий заголовок
- чітко відображає суть усіх текстів
- без лапок
- без пояснень, коментарів чи списків
- без абстрактних слів типу «Різне», «Інше», «Огляд теми»

### Формат відповіді

* У відповіді подай **виключно назву теми одним рядком**.
* **Без заголовків, списків, коментарів або пояснень.**

Набір текстів для формування спільної теми:"""
# Поверни лише назву тематики одним рядком.
#     prompt = """Завдання:
# Дай розгорнуту назву теми для наступного набору текстів, розділених за допомогою '---'.
# Відповідь надай українською мовою.
# Тексти для визначення теми:

# """
    sampling_params = SamplingParamsRequest(temperature=0.2, max_tokens=128)
    request_data: ChatRequest = ChatRequest(texts=texts, prompt=prompt, sampling_params=sampling_params)
    print(f"🧐 Generating titles for {len(texts)} clusters")

    response = requests.post(f"{LLM_SERVER_ADDRESS}/generate", json=request_data.model_dump(), timeout=REQUEST_TIMEOUT)
    raw_data = response.json()
    titles = []
    if response.status_code == 200:
        model_answer = BatchResponse.model_validate(raw_data)
        titles = [answer.text for answer in model_answer.results]
        # print(model_answer)
    return titles


def get_cluster_summary(texts: list[str]):
    prompt = """**Ти — система автоматичного формування інформаційних довідок на основі новинних кластерів.**

Ти отримуєш набір текстів, розділених рядком `\n---\n`.

Усі тексти належать до **однієї тематики**, описують **ті самі або тісно пов’язані події** та можуть частково дублювати або уточнювати одне одного.

---

### Завдання

На основі всього кластера підготуй **коротку довідку українською мовою**, яка **фактологічно узагальнює інформацію**, без оцінок і інтерпретацій.

---

### Вимоги до змісту

* Довідка має **точно та стисло передавати головні факти**.
* Зосереджуйся на:

  * події або процесі,
  * ключових фактах і діях,
  * учасниках (якщо вказані),
  * місці та часі (якщо вказані),
  * безпосередніх причинах або підставах **лише якщо вони прямо зазначені в текстах**.
* Інформація з різних текстів має бути **узгоджено об’єднана**, без повторів і суперечностей.

---

### Стиль і форма

* Мова: **українська** (обов’язково).
* Стиль: **нейтральний, інформативний, довідковий**.
* Без емоцій, оцінок, риторики, прогнозів або висновків.
* Довжина: **2–3 абзаци**, у кожному **3–5 переважно простих речень**.
* Використовуй **Markdown-жирний** текст для виділення іменованих сутностей (особи, організації, географічні назви, події).

---

### Суворі заборони (критично важливо)

* **Заборонено додавати будь-яку інформацію, якої немає в оригінальних текстах**, навіть якщо вона здається логічною або загальновідомою.
* **Не роби припущень** щодо:

  * осіб,
  * ролей,
  * дат,
  * причин,
  * країн,
  * географічних назв,
  * наслідків чи мотивів.
* **Не вигадуй імена або назви**:

  * якщо суб’єкт не названий у тексті — залишай його неназваним;
  * не уточнюй і не конкретизуй те, що в оригіналі подано узагальнено.
* **Не інтерпретуй** події і **не пояснюй** їх причин або значення, якщо цього прямо немає в текстах.
* **Не припускай**, що подія стосується України, **якщо це не зазначено явно**.
* Якщо іменовані сутності подані іншою мовою — **переклади їх українською**, без зміни змісту.

---

### Контекст

* Враховуй, що з **24 лютого 2022 року** між **Росією та Україною** триває війна, однак **використовуй цей контекст лише тоді, коли він прямо присутній у текстах**.

---

### Формат відповіді

* У відповіді подай **виключно текст довідки**.
* **Без заголовків, маркерів, пояснень або коментарів.**

Набір текстів для формування довідки:"""

    sampling_params = SamplingParamsRequest(temperature=0.2, max_tokens=2048)
    request_data: ChatRequest = ChatRequest(texts=texts, prompt=prompt, sampling_params=sampling_params)
    print(f"🧐 Generating summaries for {len(texts)} clusters")

    response = requests.post(f"{LLM_SERVER_ADDRESS}/generate", json=request_data.model_dump(), timeout=REQUEST_TIMEOUT)
    raw_data = response.json()
    summaries: list[str] = []
    if response.status_code == 200:
        model_answer = BatchResponse.model_validate(raw_data)
        summaries = [answer.text for answer in model_answer.results]
    return summaries


def get_input_filename(default="local.data.json"):
    if len(sys.argv) > 1:
        return sys.argv[1]
    return default


def get_embeddings(texts: list[str]):
    request_data: EmbeddingRequest = EmbeddingRequest(texts=texts)
    response = requests.post(f"{EMBEDDING_SERVER_ADDRESS}/embed", json=request_data.model_dump(), timeout=REQUEST_TIMEOUT)
    raw_data = response.json()
    data = EmbeddingResponse.model_validate(raw_data)
    embeddings = np.array(data.embeddings, dtype=np.float32)  # 🔥 відновлення типу
    return embeddings


def main():
    data_file = get_input_filename()
    print(f"Using data from file {data_file}")
    messages = load_json_file(data_file)

    print("ℹ️ Calculating embeddings...")
    embeddings = get_embeddings([msg.text for msg in messages])

    min_cluster_size = int(os.getenv("MIN_CLUSTER_SIZE", "7"))
    min_samples = int(os.getenv("MIN_SAMPLES", "3"))
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,  # мін. розмір кластера
        min_samples=min_samples,           # чутливість до шуму

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
        # cluster_selection_method="leaf"
    )
    print(f"""ℹ️ Clustering parameters:
- minimum cluster size: {min_cluster_size}
- minimum samples count: {min_samples}""")

    labels = clusterer.fit_predict(embeddings)

    # групуємо тексти по кластерах 📦
    clusters: dict[np.int64, list[Message]] = {}
    for msg, label in zip(messages, labels):
        clusters.setdefault(label, []).append(msg)

    # сортуємо кластери за кількістю текстів (спадання ⬇️)
    sorted_clusters = sorted(
        clusters.items(),
        key=lambda item: len(item[1]),
        reverse=True
    )

    # Генерація назв та сумаризацій
    result_clusters: list[TextCluster] = []
    # not_in_cluster_messages: list[Message] = []
    for label, messages in sorted_clusters:
        if label == -1:
            # not_in_cluster_messages = messages
            continue
        # embeds = embeddings[[i for i, l in enumerate(labels) if l == label]]
        # Через маску виходить швидше
        embeds = embeddings[labels == label]

        # Формування заголовка на основі центроїда кластера (найближчий текст)
        centroid, top_texts = cluster_centroid_and_top_texts(embeds)
        top_messages = [messages[item.index] for item in top_texts]
        result_clusters.append(TextCluster(label=int(label), messages=top_messages,
                               total_count=len(messages), texts=[msg.text for msg in top_messages]))

    batch = ["\n---\n".join(cluster.texts) for cluster in result_clusters]
    if len(batch) == 0:
        print("🫤 No clusters exist")
    else:
        titles: list[str] = get_cluster_title(batch)
        # summary_batch = [f"Тема кластера:\n{title}\n\nНабір текстів для формування довідки:\n"+tb for tb, title in zip(batch, titles)]
        # summaries: list[str] = get_cluster_summary(summary_batch)
        summaries: list[str] = get_cluster_summary(batch)
        for cluster, title, summary in zip(result_clusters, titles, summaries):
            cluster.title = title
            cluster.summary = summary

        # виводимо результат 🖨️
        clusters_count = len(result_clusters)
        for index, cluster in enumerate(result_clusters, start=1):
            print(f"""\n📦 CLUSTER {index} of {clusters_count} (label: {cluster.label}) ({cluster.total_count} messages)
🖊️ {cluster.title}
🪅 {cluster.summary}

{'-'*20}""")

            # 📰 Заголовки топ-повідомлень:""")
            # for msg in cluster.messages:
            #     print(f"- {msg.title}")
            #     # print(msg.text)

    # if len(not_in_cluster_messages) != 0:
    #     print("\n🚫 Not in cluster messages:")
    #     for msg in not_in_cluster_messages[:20]:
    #         print(f"\n🗞️ {msg.text}")

    pprint(Counter(labels))


if __name__ == "__main__":
    main()
