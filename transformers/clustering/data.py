import json
from pprint import pprint

from interfaces import RawMessage
from server.models import ClusterInfo

messages = [
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


def load_json_file(file_path: str):
    """
    Завантажує дані з JSON-файлу.

    Args:
        file_path (str): Шлях до JSON-файлу.

    Returns:
        dict або list: Дані, завантажені з файлу (залежно від структури JSON).
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    messages: list[RawMessage] = []
    errors_count = 0
    for item in data:
        try:
            message = RawMessage(**item)
            messages.append(message)
        except Exception as e:
            errors_count += 1
            pprint(e)
            pprint(item)
    if errors_count != 0:
        print(f"⚠️ Errors count: {errors_count}")
    return messages


def save_to_json_file(clusters: list[ClusterInfo], titles: list[str], summaries: list[str], file_path="local.clusters.json"):
    assert len(clusters) == len(titles) == len(summaries)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(
            [
                {
                    **cluster.model_dump(mode="json"),
                    "title": title,
                    "summary": summary
                } for cluster, title, summary in zip(clusters, titles, summaries)
            ],
            ensure_ascii=False,
            indent=2)
        )
    print(f"💽 Clusters' data have been saved into file {file_path}")


if __name__ == "__main__":
    data = load_json_file("local.data.json")
