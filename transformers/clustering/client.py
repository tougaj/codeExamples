import os
import sys
from functools import partial
from typing import Callable, Optional

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
#### Supercluster’s theme: ####
<supercluster>
{supercluster}
</supercluster>""" if supercluster else ""
    supercluster_constraints = """- Use the supercluster’s theme as a context for refining the headline’s content.
- The headline should reflect the subtopic (this cluster) specifically, rather than duplicating or generalizing the supercluster’s theme.""" if supercluster else ""

    prompt = f"""### Role ###
<role>
Automatic headline generation system.
</role>

### Instruction ###
<task>
You have been provided with a set of articles, each of which is located at a separate <article>.
All articles belong to a single common topic and are thematically related (a cluster of similar articles); they describe the same or closely related events and may partially overlap or clarify one another.
Your task is to identify the common theme of these articles and formulate ONE general, clear, and understandable headline **in Ukrainian** that can be used to name them.
</task>

### Context ###
<context>
On February 24, 2022, Russia launched a full-scale military invasion of Ukraine, and the two countries are currently at war. This context is provided solely for a general understanding of the situation. Do not use it to add new facts, assessments, or interpretations that are not included in the texts.
{supercluster_context}
</context>

### Constraints ###
<constraints>
- Use grammatically correct, natural, and stylistically consistent Ukrainian without clichés or unnatural constructions.
- Ignore minor or unique details that do not recur.
- Prioritize the most frequently mentioned ideas and concepts.
- If there are several possible topics, choose the one that:
  + is mentioned most frequently
  + is the most specific (not too general)
- If the common theme is not very clear, focus on the most frequently recurring elements and summarize them without inventing new facts.
- Formulate the headline as a complete sentence or a compound noun headline in Ukrainian.
- Headline length: 10 to 20 words. Try to stay within this range.
- Use key terms from the text, summarizing or rephrasing them without copying them verbatim.
- The wording should be specific and meaningful, clearly indicating the subject or event.
- **IT IS PROHIBITED** to formulate a headline in a way that allows for ambiguous or multiple interpretations.
- Do not use generalizations without specifics (for example: “trends,” “aspects,” “issues” without clarification).
- Do not use abstract words such as “Miscellaneous,” “Other,” or “Overview of the topic.”
- The headline should reflect the main content of most articles, not individual aspects.
- The headline should be self-contained, logically clear, and understandable without additional context.
- Maintain a neutral, objective style without judgment.
- The headline MUST be written in Ukrainian.
{supercluster_constraints}
</constraints>

### Output Format ###
<format>
- It is **PROHIBITED** to use any language other than Ukrainian for the headline.
- In your reply, include **only the topic headline in a single line**.
- Your reply must contain EXACTLY ONE line of text.
- It is **PROHIBITED** to use headings, lists, comments, explanations, or quotation marks.
</format>

### Example ###
<example>
<input>
<article>Європа стикається зі зростанням цін на природний газ...</article>
<article>Енергетична криза спричинила підвищення тарифів...</article>
<article>Европа сталкивается с рекордным ростом цен на газ и угрозой деиндустриализации...</article>
<article>Europe’s energy crisis deepens as surging gas prices fuel economic uncertainty...</article>
<article>Europa kämpft mit explodierenden Gaspreisen und den Folgen für die Industrie...</article>
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
- Довідка має відображати саме підтематику (цей кластер), а не дублювати або узагальнювати назву суперкластеру.""" if supercluster else ""

    prompt = f"""
### Role ###
<role>
Система автоматичного формування інформаційних довідок на основі новинних кластерів.
</role>

### Instruction ###
<task>
Тобі надано набір статей (текстів), кожна з яких міститься в окремому <article>.
Усі статті належать до однієї спільної тематики та є змістовно пов'язаними (кластер схожих статей), описують ті самі або тісно пов'язані події, можуть частково дублювати або уточнювати одне одного.
Твоє завдання — на основі всього кластера підготувати **коротку довідку українською мовою**, яка **фактологічно узагальнює інформацію**, без оцінок і інтерпретацій.
</task>

### Context ###
<context>
24 лютого 2022 року Росія здійснила повномасштабний збройний напад на Україну, і ці дві держави перебувають у стані війни. Цей контекст надано лише для загального розуміння ситуації. Не використовуй його для додавання нових фактів, оцінок або інтерпретацій, відсутніх у текстах.
{supercluster_context}
</context>

### Constraints ###
<constraints>
- Довідка має **точно та стисло передавати ключових факти, події і тези**.
- УНИКАЙ другорядних деталей, прикладів, цитат, оцінних суджень і емоційного тону.
- Зосереджуйся на:

  + події або процесі,
  + ключових фактах і діях,
  + учасниках (якщо вказані),
  + місці та часі (якщо вказані),
  + безпосередніх причинах або підставах **лише якщо вони прямо зазначені в текстах**.

- Інформація з різних текстів має бути **узгоджено об’єднана**, без повторів і суперечностей.
- Мова: **українська** (обов’язково). Використовуй природну, зрозумілу й граматично правильну українську мову.
- Дотримуйся нейтрального, об'єктивного та інформативного стилю.
- Без емоцій, оцінок, риторики, прогнозів або висновків.
- Якщо в текстах є неоднозначна інформація, намагайся передати її максимально нейтрально, не віддаючи перевагу жодній з інтерпретацій.
- Якщо формулювання в довідці не може бути підтверджене прямою цитатою або перефразуванням фрагментів оригінальних текстів, воно вважається забороненим.
{supercluster_constraints}
</constraints>

### Strict prohibitions (critical) ###
<prohibitions>
- **ЗАБОРОНЕНО** додавати будь-яку інформацію, яка не міститься безпосередньо в оригінальних текстах (навіть якщо вона здається логічною або загальновідомою), включаючи припущення, інтерпретації, причини, мотиви, додаткові деталі, пояснення, імена, факти, дати, географічні назви тощо.
- Інформація вважається безпосередньо присутньою **лише у разі її явної текстової згадки** в текстах; інформація, що випливає з контексту, логічних міркувань або загальних знань, **вважається забороненою**.
- **ЗАБОРОНЕНО** робити припущення щодо осіб, ролей, подій, дат, причин, країн, географічних назв, фактів, наслідків чи мотивів. Якщо в тексті не вказано ім’я чи назва суб'єкту — заборонено їх вигадувати.
- **ЗАБОРОНЕНО** вигадувати імена або назви:

  - якщо суб’єкт не названий у тексті — залишай його неназваним;
  - не уточнюй і не конкретизуй те, що в оригіналі подано узагальнено.

- **ЗАБОРОНЕНО ПРИПУСКАТИ**, що в тексті йдеться про Україну, якусь область або місто України, українських політиків, українські органи влади, якщо тільки це не вказано явно в текстах.
</prohibitions>

### Output Format ###
<format>
- **ЗАБОРОНЕНО** використовувати в назві будь-яку мову, окрім української.
- У відповіді подай **виключно текст довідки**, без заголовків.
- Довжина довідки: **2–3 абзаци**, у кожному **3–5 переважно простих речень**. Намагайся дотримуватись цього діапазону.
- **ЗАБОРОНЕНО** використовувати заголовки, списки, коментарі, пояснення.
- **Використовуй** Markdown **жирний** текст для виділення іменованих сутностей (NER).
- Виділяй жирним **лише конкретні іменовані сутності**: осіб, організації, країни, міста, установи, офіційні назви подій чи документів.
</format>

### Input Data ###
<input>"""

    sampling_params = SamplingParamsRequest(temperature=0.2, max_tokens=2*1024)
    request_data: ChatRequest = ChatRequest(texts=texts, prompt=prompt, sampling_params=sampling_params)
    print(f"🧐 Generating summaries for {len(texts)} clusters")

    response = requests.post(f"{LLM_SERVER_ADDRESS}/generate", json=request_data.model_dump(), timeout=REQUEST_TIMEOUT)
    raw_data = response.json()
    summaries: list[str] = []
    if response.status_code == 200:
        model_answer = BatchResponse.model_validate(raw_data)
        summaries = [(answer.text if answer.finish_reason == "stop" else "") for answer in model_answer.results]
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


# def request_descriptions(messages: list[RawMessage], clusters: list[ClusterInfo], max_sample_len: int, supercluster: Optional[str]) -> tuple[list[str], list[str]]:
#     max_message_len = max_sample_len
#     batch = get_batch(clusters, raw_messages=messages, max_len=max_message_len)

#     titles: list[str] = []
#     while len(titles) == 0:
#         try:
#             titles: list[str] = get_cluster_title(batch, supercluster=supercluster)
#         except Exception as e:
#             print(e)
#             max_message_len -= 100
#             if max_message_len <= 100:
#                 raise RuntimeError("Unable to generate titles")
#             batch = get_batch(clusters, raw_messages=messages, max_len=max_message_len)

#     # summaries: list[str] = ["" for _ in clusters]  # 🪲 for debug
#     summaries: list[str] = []
#     while len(summaries) == 0:
#         try:
#             summaries: list[str] = get_cluster_summary(batch, supercluster=supercluster)
#         except Exception as e:
#             print(e)
#             max_message_len -= 100
#             if max_message_len <= 100:
#                 raise RuntimeError("Unable to generate summaries")
#             batch = get_batch(clusters, raw_messages=messages, max_len=max_message_len)

#     return titles, summaries


def _generate_with_retry(
    generate_fn: Callable[[list[str]], list[str]],
    clusters: list[ClusterInfo],
    messages: list[RawMessage],
    max_len: int,
    min_len: int = 100,
    step: int = 100,
) -> list[str]:
    if max_len <= min_len:
        raise RuntimeError(f"Unable to generate: max_len exhausted")

    # 1️⃣ Спроба згенерувати batch і отримати результат
    batch = get_batch(clusters, raw_messages=messages, max_len=max_len)
    try:
        results = generate_fn(batch)
    except Exception as e:
        print(e)
        return _generate_with_retry(generate_fn, clusters, messages, max_len - step, min_len, step)

    # 2️⃣ Знаходимо індекси порожніх результатів
    empty_indices = [i for i, r in enumerate(results) if not r]
    if not empty_indices:
        return results

    print(f"🤐 Content generation error for {len(empty_indices)} item(s)")
    # 3️⃣ Рекурсивно перегенеровуємо тільки проблемні елементи
    failed_clusters = [clusters[i] for i in empty_indices]
    regenerated = _generate_with_retry(generate_fn, failed_clusters, messages, max_len - step, min_len, step)

    # 4️⃣ Вставляємо на правильні місця
    for idx, value in zip(empty_indices, regenerated):
        results[idx] = value

    return results


def request_descriptions(
    messages: list[RawMessage],
    clusters: list[ClusterInfo],
    max_sample_len: int,
    supercluster: Optional[str],
) -> tuple[list[str], list[str]]:
    titles = _generate_with_retry(
        partial(get_cluster_title, supercluster=supercluster),
        clusters, messages, max_sample_len,
    )
    summaries = _generate_with_retry(
        partial(get_cluster_summary, supercluster=supercluster),
        clusters, messages, max_sample_len,
    )
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
    titles, summaries = request_descriptions(messages=messages, clusters=clusters, max_sample_len=MAX_TEXT_LEN, supercluster=supercluster)

    print_clusters(clusters=clusters, titles=titles, summaries=summaries)


if __name__ == "__main__":
    main()
