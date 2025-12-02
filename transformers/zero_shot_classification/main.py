import json
from pathlib import Path
from time import time
from typing import List, NotRequired, TypedDict

from utils import classify_messages


class Message(TypedDict):
    title: str
    body: str
    translated_title: NotRequired[str]
    translated_body: NotRequired[str]


def get_messages_from_file(file_path: Path):
    data: List[Message] = []
    with file_path.open(encoding='utf-8') as f:
        try:
            data = json.load(f)
            if not isinstance(data, list):
                data = [data]
        except Exception as e:
            print(f"Error reading file {file_path}: {e}. Most likely, the file has an incorrect format.")
    return data


def get_data_for_classification(messages: List[Message]):
    data: List[str] = []
    for message in messages:
        # title = message.get("translated_title") or message.get("title")
        # temp_body = message.get("translated_body") or message.get("body")[:500]
        title = message.get("title")
        temp_body = message.get("body")[:500]
        body = temp_body if len(temp_body) < 500 else temp_body[:temp_body.rfind(" ")]
        data.append(f"{title}\n{body}")
    return data


def get_all_messages():
    json_files = list(Path("local.data").glob("*.json"))
    original_messages: List[Message] = []
    for file in json_files:
        original_messages += get_messages_from_file(file)
    return original_messages


def main():
    original_messages = get_all_messages()
    messages_count = len(original_messages)
    if messages_count == 0:
        return
    data = get_data_for_classification(original_messages)
    print(f"Found {len(data)} messages")
    execution_time = classify_messages(data, [(m.get("translated_body") or "")[:500]+'...' for m in original_messages])
    print(f"⏱️ Classification took {execution_time:.2f} seconds ({execution_time/messages_count:.2f} sec/msg)")


if __name__ == "__main__":
    main()
