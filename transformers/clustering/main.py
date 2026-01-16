import sys
from collections import Counter
from pprint import pprint

import hdbscan
import numpy as np
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from data import load_json_file
from interfaces import (BatchResponse, ChatRequest, Message,
                        SamplingParamsRequest, TextCluster, TopText)

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
    sampling_params = SamplingParamsRequest(temperature=0.5, max_tokens=128)
    request_data: ChatRequest = ChatRequest(texts=texts, prompt=prompt, sampling_params=sampling_params)
    print(f"🧐 Generating titles for {len(texts)} clusters")

    response = requests.post(f"{SERVER_ADDRESS}/generate", json=request_data.model_dump(), timeout=REQUEST_TIMEOUT)
    raw_data = response.json()
    titles = []
    if response.status_code == 200:
        model_answer = BatchResponse.model_validate(raw_data)
        titles = [answer.text for answer in model_answer.results]
        # print(model_answer)
    return titles


def get_cluster_summary(texts: list[str]):
    #     prompt = """Ти — система створення новинних резюме.

    # Отримуєш набір текстів, розділених рядком \n---\n.

    # Усі тексти належать до однієї спільної тематики та є змістовно пов’язаними (кластер схожих статей).

    # Твоє завдання — підготувати резюме **українською мовою**, дотримуючись таких правил:

    # - Резюме має **обов'язково** бути українською мовою!.
    # - **Передай головний зміст точно й стисло** — зосередься на ключових фактах, подіях і тезах.
    # - Якщо в тексті є **основні учасники, місце, час, причина події**, зазнач це.
    # - **Уникай** другорядних деталей, прикладів, цитат, оцінних суджень і емоційного тону.
    # - Дотримуйся **нейтрального, об'єктивного та інформативного стилю.**
    # - Використовуй **природну, зрозумілу й граматично правильну** українську мову.
    # - Довжина резюме має бути від 2 до 3 абзаців, кожен з яких містить від 3 до 5 бажано простих речень.
    # - **У відповіді подай лише резюме** — без коментарів, пояснень, заголовків.
    # - **Заборонено додавати інформацію, якої немає в оригіналі**, навіть якщо вона здається очевидною або логічною за контекстом.
    # - **Не роби припущень** щодо осіб, подій, дат, країн, географічних назв чи фактів. Якщо в тексті не вказано ім’я чи назва суб'єкту — не вигадуй його.
    # - **Не додавай** жодних імен, ролей, подій чи фактів, яких **немає в оригіналі**. Якщо в оригіналі немає конкретної назви або імені — **не вигадуй їх**, навіть якщо це звучить природніше.
    # - **Заборонено** додавати вигадані імена, факти, уточнення, дати, країни, географічні назви, інтерпретації чи пояснення.
    # - **Не інтерпретуй** і не додавай причин, мотивів чи додаткових деталей, яких немає в тексті.
    # - Якщо в оригіналі іменовані сутності іншою мовою — **переклади їх українською**.
    # - **Заборонено припускати**, що в тексті йдеться про Україну, якщо тільки це не вказано явно в оригіналі.
    # - Враховуй те, що 24 лютого 2022 року Росія агресивно напала на Україну з метою знищення української державності і наразі ці дві країни знаходяться в стані війни.
    # - Використовуй Markdown **жирний** текст для виділення іменованих сутностей (NER).

    # Набір текстів:"""

    #     prompt = """**Ти — система автоматичного формування інформаційних довідок на основі новинних кластерів.**

    # Ти отримуєш:

    # 1. **Тему кластера** (згенеровану окремо).
    # 2. Набір текстів, розділених рядком `\n---\n`.

    # Усі тексти належать до **однієї тематики**, описують **ті самі або тісно пов’язані події** та можуть частково дублювати або уточнювати одне одного.

    # ---

    # ### Тема кластера

    # Тема передається окремо і використовується **лише як орієнтир для фокусу та формулювань**.

    # * Тема **не є джерелом фактів**.
    # * **Заборонено** додавати будь-яку інформацію з теми, якщо вона **не підтверджується текстами**.
    # * Якщо між темою і текстами є суперечність — **пріоритет мають тексти**.
    # * Якщо тема:

    #   * **ширша**, ніж зміст текстів — узагальнюй лише підтверджену інформацію;
    #   * **вужча** або містить деталі, яких немає в текстах — **ігноруй ці деталі**.

    # ---

    # ### Завдання

    # На основі **всіх текстів кластера** підготуй **коротку інформаційну довідку українською мовою**, яка **фактологічно узагальнює інформацію** та **узгоджена з темою за змістом і акцентами**, не виходячи за межі наданих текстів.

    # ---

    # ### Вимоги до змісту

    # * Передай **головні факти стисло й точно**.
    # * Зосереджуйся на:

    #   * події або процесі;
    #   * ключових фактах і діях;
    #   * учасниках (якщо прямо вказані);
    #   * місці та часі (якщо прямо вказані);
    #   * причинах або підставах **лише якщо вони прямо зазначені в текстах**.
    # * Узгоджуй інформацію з різних текстів, **уникаючи повторів і суперечностей**.

    # ---

    # ### Стиль і форма

    # * Мова: **українська** (обов’язково).
    # * Стиль: **нейтральний, об’єктивний, довідковий**.
    # * Без емоцій, оцінок, прогнозів, висновків або риторики.
    # * Довжина: **2–3 абзаци**, кожен з яких містить **3–5 переважно простих речень**.
    # * Використовуй Markdown **жирний** текст для виділення іменованих сутностей (особи, організації, географічні назви, події).

    # ---

    # ### Суворі заборони (критично важливо)

    # * **Заборонено додавати будь-яку інформацію, якої немає в текстах**, навіть якщо вона здається очевидною або логічною.
    # * **Не роби припущень** щодо:

    #   * осіб, ролей, дат, причин, країн, географічних назв, мотивів або наслідків.
    # * **Не вигадуй імена або назви**:

    #   * якщо суб’єкт не названий у текстах — залишай його неназваним;
    #   * не уточнюй і не конкретизуй узагальнені формулювання з оригіналу.
    # * **Не інтерпретуй** події та **не пояснюй** їх значення.
    # * **Не припускай**, що подія стосується України, якщо це **не зазначено явно**.
    # * Якщо іменовані сутності подані іншою мовою — **переклади їх українською**, без зміни змісту.

    # ---

    # ### Контекст

    # * Враховуй, що з **24 лютого 2022 року** між **Росією та Україною** триває війна, **але використовуй цей контекст лише тоді, коли він прямо присутній у текстах**.

    # ---

    # ### Самоконтроль перед відповіддю

    # Перед формуванням довідки переконайся, що:

    # * кожне твердження можна підтвердити щонайменше одним із текстів;
    # * тема використана **лише як контекстний орієнтир**, а не як джерело фактів.

    # ---

    # ### Формат відповіді

    # * У відповіді подай **виключно текст довідки**.
    # * **Без заголовків, списків, коментарів або пояснень.**"""

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

    sampling_params = SamplingParamsRequest(temperature=0.5, max_tokens=2048)
    request_data: ChatRequest = ChatRequest(texts=texts, prompt=prompt, sampling_params=sampling_params)
    print(f"🧐 Generating summaries for {len(texts)} clusters")

    response = requests.post(f"{SERVER_ADDRESS}/generate", json=request_data.model_dump(), timeout=REQUEST_TIMEOUT)
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


def main():
    data_file = get_input_filename()
    print(f"Using data from file {data_file}")
    messages = load_json_file(data_file)
    # for text in data:
    #     text["text"] = get_text(text)
    # texts = [get_text(item) for item in data]
    # texts = [remove_html_tags(text)[:1000] for text in messages]

    # Завантажити локальну модель можна так (тут вказується каталог, де знаходиться config.json):
    # model = SentenceTransformer("/data/hf_home/hub/models--google--embeddinggemma-300m/snapshots/57c266a740f537b4dc058e1b0cda161fd15afa75")
    model = SentenceTransformer(
        # "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        # "sentence-transformers/all-MiniLM-L6-v2"
        "google/embeddinggemma-300m"
        # "Qwen/Qwen3-Embedding-0.6B"
        # "Qwen/Qwen3-Embedding-8B"
        # , local_files_only=True # ⚠️ For using local model
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
        min_samples=7,           # чутливість до шуму

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

    # Генерація назв та сумаризацій
    result_clusters: list[TextCluster] = []
    not_in_cluster_messages: list[Message] = []
    for label, messages in sorted_clusters:
        if label == -1:
            not_in_cluster_messages = messages
            continue
        texts = [msg.text for msg in messages]
        embeds = embeddings[[i for i, l in enumerate(labels) if l == label]]

        # Формування заголовка на основі центроїда кластера (найближчий текст)
        centroid, title_text, top = cluster_centroid_and_top_texts(texts, embeds)
        top_messages = [messages[item.index] for item in top]
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
🪅 {cluster.summary}""")

    # if len(not_in_cluster_messages) != 0:
    #     print("\n🚫 Not in cluster messages:")
    #     for msg in not_in_cluster_messages[:20]:
    #         print(f"\n🗞️ {msg.text}")

    # 📰 Заголовки топ-повідомлень:""")
    #         for msg in cluster.messages:
    #             print(f"- {msg.title}")
    #             # print(msg.text)

    pprint(Counter(labels))


if __name__ == "__main__":
    main()
