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
SUPERCLUSTER = os.getenv("SUPERCLUSTER")
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
#### Supercluster: ####
<supercluster>
{supercluster}
</supercluster>""" if supercluster else ""
    supercluster_constraints = """- Use the supercluster only to clarify context, without duplicating its content.
- The brief must reflect the specific subtopic (this cluster), not duplicate or generalize the supercluster content.""" if supercluster else ""

    prompt = f"""
### Role
<role>
System for automatic generation of informational briefs based on news clusters.
</role>

### Instruction
<task>
You are given a set of articles (texts), each contained within a separate <article>.
All articles belong to a common topic and are semantically related (a cluster of similar articles), describing the same or closely related events, and may partially duplicate or clarify each other.
Your task is to produce a **concise informational brief in Ukrainian**, which **factually summarizes the information** without evaluations or interpretations.
</task>

### Context
<context>
On February 24, 2022, Russia launched a full-scale armed invasion of Ukraine, and the two states are in a state of war. This context is provided only for general understanding. Do not use it to add new facts, evaluations, or interpretations that are not present in the texts.
{supercluster_context}
</context>

### Constraints
<constraints>
- The brief must accurately and concisely convey key facts, events, and statements.
- Focus on:

  + the event or process,
  + key facts and actions,
  + participants (if specified),
  + place and time (if specified),
  + causes or grounds — only if explicitly stated in the texts.

- Information from different texts must be merged into a single coherent brief.
- In case of contradictions, present information neutrally without choosing one version.
- Avoid repeating identical facts.
- Use Ukrainian language: natural, clear, and grammatically correct.
- Maintain a neutral, objective, and informative style.
- Avoid secondary details, examples, quotations, and unnecessary clarifications.
- Brevity must not lead to loss of key facts.
- If information is insufficient — omit the corresponding aspects without explanation.
- The brief MUST be written in Ukrainian.
{supercluster_constraints}
</constraints>

### Strict prohibitions (critical)
<prohibitions>
- It is prohibited to add any information not present in the texts, including:
  assumptions, interpretations, causes, motives, additional details, names, dates, geographical names.
- Every statement must be directly based on the texts and verifiable through them.
  Paraphrasing and generalization are allowed without adding new facts.

- It is prohibited to:

  * make assumptions about persons, events, roles, or circumstances,
  * clarify or specify generalized statements from the text,
  * invent names or titles.

- If a subject is not named — leave it unnamed.
- It is prohibited to assume geographical or political context (including Ukraine),
  unless it is explicitly stated in the texts.
</prohibitions>

### Execution Rules
<rules>
DO:
- Merge information from multiple texts into a single narrative.
- Paraphrase for brevity and to eliminate repetition.
- Preserve key facts during summarization.
- Build a logically consistent and coherent narrative.

DO NOT:
- Do not duplicate identical facts.
- Do not add explanations or context beyond the texts.
- Do not use emotional or evaluative language.

WHEN INFORMATION IS LIMITED:
- Omit missing details.

WHEN INFORMATION CONFLICTS:
- Generalize without detailing and without choosing a single version.
</rules>

### Micro-structure
<micro_structure>
Start the brief with a description of the main event or process.
Structure the brief in the following logical order (if information is available in the texts):

1. Main event or subject:
  - what happened or is happening.

2. Key participants and their actions:
  - who is involved and what actions they take.

3. Clarifying details:
  - time, place, conditions, quantitative indicators, or other factual circumstances.

4. Additional facts (if available):
  - consequences or related events, if explicitly mentioned in the texts.

Do not include an element if the corresponding information is missing from the texts.
Follow this order unless it contradicts the content of the texts.
</micro_structure>

### Output Format
<format>
- It is **STRICTLY PROHIBITED** to use any language other than Ukrainian for writing the brief.
- Provide **only the brief text**, without headings.
- Length: **2–3 paragraphs**, each with **3–5 sentences**. Try to stay within this range. Prefer simple and moderately complex sentences without excessive complexity.
- It is **PROHIBITED** to use headings, lists, comments, or explanations.
- **MUST** use **bold** Markdown text to highlight the following named entities (NER): people, organizations, countries, cities, institutions, and official names of events or documents.
- Highlight each named entity in bold on first mention. Repeated mentions may remain unhighlighted.
- Do not highlight unnecessary or generic words as named entities.
</format>

### Input Data
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
        raise RuntimeError(f"Unable to generate: {max_len} exhausted")

    # 1️⃣ Спроба згенерувати batch і отримати результат
    batch = get_batch(clusters, raw_messages=messages, max_len=max_len)
    try:
        results = generate_fn(batch)
    except Exception as e:
        print(f"🤔 Content generation error (maximum text length is {max_len}): {e}")
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


def print_clusters(clusters: list[ClusterInfo], titles: list[str], summaries: list[str], original_messages_count: int):
    clusters_count = len(clusters)
    assert clusters_count == len(titles) == len(summaries)
    for index, (cluster, title, summary) in enumerate(zip(clusters, titles, summaries), start=1):
        msg_count = len(cluster.similarity)
        # виводимо результат 🖨️
        print(f"""\n📦 CLUSTER {index} of {clusters_count} (label: {cluster.label}) ({msg_count} messages, {msg_count/original_messages_count*100:.1f} %)
🖊️ {title}
🪅 {summary}

{'-'*20}""")


def main():
    data_file = get_input_filename()
    messages = load_json_file(data_file)

    print(f"""⚙️ Clustering messages using configuration:
  - data from file: {data_file}
  - messages count: {len(messages)}
  - minimum cluster size: {min_cluster_size}
  - minimum samples: {min_samples}
  - supercluster: {SUPERCLUSTER}
""")

    # print("🔍 Calculating embeddings...")
    # embeddings = request_embeddings([msg.get_text(MAX_TEXT_LEN) for msg in messages])

    # print("🔍 Looking up for clusters...")
    # clusters = request_clusters([msg.id for msg in messages], embeddings=embeddings, min_cluster_size=min_cluster_size, min_samples=min_samples)

    print("🔍 Looking up for clusters...")
    clusters = request_text_clusters(messages, min_cluster_size=min_cluster_size, min_samples=min_samples)

    if len(clusters) == 0:
        print("🫤 No clusters exist")
        return

    titles, summaries = request_descriptions(messages=messages, clusters=clusters, max_sample_len=MAX_TEXT_LEN, supercluster=SUPERCLUSTER)

    print_clusters(clusters=clusters, titles=titles, summaries=summaries, original_messages_count=len(messages))


if __name__ == "__main__":
    main()
