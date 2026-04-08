import os
import sys
# from collections import Counter
# from pprint import pprint
from typing import Optional

import numpy as np
import requests
from dotenv import load_dotenv
from pydantic import TypeAdapter

from data import load_json_file
from interfaces import (BatchResponse, ChatRequest, MessageId, RawMessage,
                        SamplingParamsRequest)
from server.models import (ClusterInfo, ClusteringRequest,
                           ClusteringTextRequest, EmbeddingRequest,
                           EmbeddingResponse, MessageForClustering)

load_dotenv()

EMBEDDING_SERVER_ADDRESS = os.getenv("EMBEDDING_SERVER", "http://127.0.0.1:8000")
LLM_SERVER_ADDRESS = os.getenv("LLM_SERVER", "http://127.0.0.1:8000")
REQUEST_TIMEOUT = int(os.getenv("REQUESTS_TIMEOUT", "300"))
min_cluster_size = int(os.getenv("MIN_CLUSTER_SIZE", "7"))
min_samples = int(os.getenv("MIN_SAMPLES", "")) if os.getenv("MIN_SAMPLES") else None
MAX_TEXT_LEN = 2000


def print_centroid_message_info(messages: list[RawMessage], index: int):
    message = messages[index]
    print(f"🖊️ {message.title}")
    # print(f"📰 {message["text"]}")


def get_cluster_title(texts: list[str], supercluster: Optional[str] = None):
    supercluster_context = f"""
#### Суперкластер: ####
<supercluster>
{supercluster}
</supercluster>""" if supercluster else ""
    supercluster_constraints = """- Враховуй тематику суперкластеру як контекст для уточнення змісту заголовка.
- Заголовок має відображати саме підтематику (цей кластер), а не дублювати або узагальнювати назву суперкластеру.
- За потреби використовуй терміни із суперкластеру, якщо вони допомагають точніше описати підтематику.""" if supercluster else ""

    prompt = f"""### Role ###
<role>
Система автоматичного створення заголовків.
</role>

### Instruction ###
<task>
Тобі надано набір статей, кожна з яких міститься в окремому <article>.
Усі статті належать до однієї спільної тематики та є змістовно пов'язаними (кластер схожих статей), описують ті самі або тісно пов'язані події, можуть частково дублювати або уточнювати одне одного.
Твоє завдання — визначити спільну тему цих статей та сформулювати ОДИН узагальнений, чіткий та зрозумілий заголовок **українською мовою**, яким можна їх озаглавити.
</task>

### Context ###
<context>
24 лютого 2022 року Росія здійснила повномасштабний збройний напад на Україну, і ці дві держави перебувають у стані війни. Використовуй цей контекст лише тоді, коли він прямо присутній у статтях.
{supercluster_context}
</context>

### Constraints ###
<constraints>
- Використовуй граматично правильну, природну та стилістично узгоджену українську мову без кальок і неприродних конструкцій.
- Ігноруй другорядні або унікальні деталі, що не повторюються.
- Пріоритезуй найчастіше згадувані ідеї та концепти.
- Якщо є кілька можливих тем, обери ту, що:
  + найчастіше повторюється
  + є найбільш конкретною (не надто загальною)
- Якщо спільна тема слабко виражена, орієнтуйся на найбільш повторювані елементи та узагальни їх без вигадування нових фактів.
- Сформулюй заголовок як повне речення або складний іменниковий заголовок українською мовою.
- Довжина заголовка: від 10 до 20 слів. Намагайся дотримуватись цього діапазону.
- Використовуй ключові терміни з текстів, узагальнюючи або перефразовуючи їх без дослівного копіювання.
- Формулювання має бути конкретним і змістовним, з чітким зазначенням предмета або події.
- **ЗАБОРОНЕНО** формулювати заголовок таким чином, який допускає двозначне або неоднозначне тлумачення.
- Не використовуй узагальнення без конкретики (наприклад: "тенденції", "аспекти", "питання" без уточнення).
- Не використовуй абстрактні слова типу «Різне», «Інше», «Огляд теми».
- Заголовок має відображати основний зміст більшості статей, а не окремі аспекти.
- Заголовок має бути самодостатнім, логічно ясним і зрозумілим без додаткового контексту.
- Дотримуйся нейтрального, об'єктивного стилю без оцінок.
- Заголовок ОБОВ'ЯЗКОВО має бути написаний українською мовою.
{supercluster_constraints}
</constraints>

### Output Format ###
<format>
- У відповіді подай **виключно заголовок теми одним рядком**.
- Відповідь має містити РІВНО ОДИН рядок тексту.
- **ЗАБОРОНЕНО** використовувати заголовки, списки, коментарі, пояснення, лапки.
</format>

### Example ###
<example>
<input>
<article>Європа стикається зі зростанням цін на природний газ...</article>
<article>Енергетична криза спричинила підвищення тарифів...</article>
</input>

<answer>
Зростання цін на газ та енергетична криза в Європі та їх економічні наслідки
</answer>
</example>

### Input Data ###
<input>"""
# - повне речення або складний іменниковий заголовок українською мовою;
# - чітко відображає суть усіх текстів.
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
    else:
        raise ValueError(response.text)
    return titles


def get_cluster_summary(texts: list[str], supercluster: Optional[str] = None):
    supercluster_context = f"""
#### Суперкластер: ####
<supercluster>
{supercluster}
</supercluster>""" if supercluster else ""
    supercluster_constraints = """- Враховуй тематику суперкластеру як контекст для уточнення змісту заголовка.
- Заголовок має відображати саме підтематику (цей кластер), а не дублювати або узагальнювати назву суперкластеру.
- За потреби використовуй терміни із суперкластеру, якщо вони допомагають точніше описати підтематику.""" if supercluster else ""

    prompt = f"""**Ти — система автоматичного формування інформаційних довідок на основі новинних кластерів.**

Тобі надано набір статей, кожна з яких міститься в окремому <article>.
Усі статті належать до однієї спільної тематики та є змістовно пов'язаними (кластер схожих статей), описують ті самі або тісно пов'язані події, можуть частково дублювати або уточнювати одне одного.

---

### Завдання

На основі всього кластера підготуй **коротку довідку українською мовою**, яка **фактологічно узагальнює інформацію**, без оцінок і інтерпретацій.

---

### Context ###
<context>
24 лютого 2022 року Росія здійснила повномасштабний збройний напад на Україну, і ці дві держави перебувають у стані війни. Використовуй цей контекст лише тоді, коли він прямо присутній у статтях.
{supercluster_context}
</context>

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
{supercluster_constraints}

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

### Формат відповіді

* У відповіді подай **виключно текст довідки**.
* **Без заголовків, маркерів, пояснень або коментарів.**

Набір текстів для формування довідки:
<input>"""

    sampling_params = SamplingParamsRequest(temperature=0.2, max_tokens=2048)
    request_data: ChatRequest = ChatRequest(texts=texts, prompt=prompt, sampling_params=sampling_params)
    print(f"🧐 Generating summaries for {len(texts)} clusters")

    response = requests.post(f"{LLM_SERVER_ADDRESS}/generate", json=request_data.model_dump(), timeout=REQUEST_TIMEOUT)
    raw_data = response.json()
    summaries: list[str] = []
    if response.status_code == 200:
        model_answer = BatchResponse.model_validate(raw_data)
        summaries = [answer.text for answer in model_answer.results]
    else:
        raise ValueError(response.text)
    return summaries


def get_input_filename(default="local.data.json"):
    if len(sys.argv) > 1:
        return sys.argv[1]
    return default


def request_embeddings(texts: list[str]) -> np.ndarray:
    request_data = EmbeddingRequest(texts=texts)
    response = requests.post(f"{EMBEDDING_SERVER_ADDRESS}/embed", json=request_data.model_dump(), timeout=REQUEST_TIMEOUT)
    raw_data = response.json()
    data = EmbeddingResponse.model_validate(raw_data)
    embeddings = np.array(data.embeddings, dtype=np.float32)  # 🔥 відновлення типу
    return embeddings


def request_clusters(ids: list[str], embeddings: np.ndarray, min_cluster_size: int, min_samples: Optional[int]) -> list[ClusterInfo]:
    assert len(ids) == len(embeddings)
    request_data = ClusteringRequest(ids=ids, embeddings=embeddings.tolist(), min_cluster_size=min_cluster_size,
                                     min_samples=min_samples, ignore_empty_cluster=True)
    response = requests.post(f"{EMBEDDING_SERVER_ADDRESS}/clusters", json=request_data.model_dump(), timeout=REQUEST_TIMEOUT)
    raw_data = response.json()
    clusters = TypeAdapter(list[ClusterInfo]).validate_python(raw_data)
    # Можна і так, але це менш "pydantic-way"
    # clusters = [ClusterInfo(**item) for item in raw_data]
    return clusters


def request_text_clusters(messages: list[RawMessage],  min_cluster_size: int, min_samples: Optional[int]) -> list[ClusterInfo]:
    request_data = ClusteringTextRequest(
        messages=[MessageForClustering(id=msg.id, text=msg.get_text(MAX_TEXT_LEN)) for msg in messages],
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        ignore_empty_cluster=True)
    response = requests.post(f"{EMBEDDING_SERVER_ADDRESS}/text_clusters", json=request_data.model_dump(), timeout=REQUEST_TIMEOUT)
    raw_data = response.json()
    clusters = TypeAdapter(list[ClusterInfo]).validate_python(raw_data)
    # Можна і так, але це менш "pydantic-way"
    # clusters = [ClusterInfo(**item) for item in raw_data]
    return clusters


def get_batch(clusters: list[ClusterInfo], raw_messages: list[RawMessage], max_len: int, top_k=10):
    messages: dict[MessageId, RawMessage] = {}
    for msg in raw_messages:
        messages[msg.id] = msg
    texts: list[str] = []
    for cluster in clusters:
        top_texts = [f"""<article>
{messages[sim.id].get_text(max_len)}
</article>""" for sim in cluster.similarity[:top_k]]
        texts.append("\n".join(top_texts))
    return texts


def request_descriptions(messages: list[RawMessage], clusters: list[ClusterInfo], supercluster: Optional[str]) -> tuple[list[str], list[str]]:
    max_message_len = MAX_TEXT_LEN
    batch = get_batch(clusters, raw_messages=messages, max_len=max_message_len)

    titles: list[str] = []
    while len(titles) == 0:
        try:
            titles: list[str] = get_cluster_title(batch, supercluster=supercluster)
        except Exception as e:
            print(e)
            max_message_len -= 100
            if max_message_len <= 100:
                raise RuntimeError("Unable to generate titles")
            batch = get_batch(clusters, raw_messages=messages, max_len=max_message_len)

    # summaries: list[str] = ["" for _ in clusters]  # 🪲 for debug
    summaries: list[str] = []
    while len(summaries) == 0:
        try:
            summaries: list[str] = get_cluster_summary(batch, supercluster=supercluster)
        except Exception as e:
            print(e)
            max_message_len -= 100
            if max_message_len <= 100:
                raise RuntimeError("Unable to generate summaries")
            batch = get_batch(clusters, raw_messages=messages, max_len=max_message_len)

    return titles, summaries


def print_clusters(clusters: list[ClusterInfo], titles: list[str], summaries: list[str]):
    clusters_count = len(clusters)
    assert clusters_count == len(titles) == len(summaries)
    for index, (cluster, title, summary) in enumerate(zip(clusters, titles, summaries), start=1):
        # виводимо результат 🖨️
        print(f"""\n📦 CLUSTER {index} of {clusters_count} (label: {cluster.label}) ({len(cluster.similarity)} messages)
🖊️ {title}
🪅 {summary}

{'-'*20}""")


def main():
    data_file = get_input_filename()
    print(f"Using data from file {data_file}")
    messages = load_json_file(data_file)

    # print("ℹ️ Calculating embeddings...")
    # embeddings = request_embeddings([msg.get_text(MAX_TEXT_LEN) for msg in messages])

    # print("ℹ️ Looking up for clusters...")
    # clusters = request_clusters([msg.id for msg in messages], embeddings=embeddings, min_cluster_size=min_cluster_size, min_samples=min_samples)

    print("ℹ️ Looking up for clusters...")
    clusters = request_text_clusters(messages, min_cluster_size=min_cluster_size, min_samples=min_samples)

    if len(clusters) == 0:
        print("🫤 No clusters exist")
        return

    supercluster = os.getenv("SUPERCLUSTER")
    titles, summaries = request_descriptions(messages=messages, clusters=clusters, supercluster=supercluster)

    print_clusters(clusters=clusters, titles=titles, summaries=summaries)


if __name__ == "__main__":
    main()
