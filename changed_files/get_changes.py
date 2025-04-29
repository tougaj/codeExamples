#!/usr/bin/env python3

import argparse


def read_snapshot(file_path):
    data = {}
    with open(file_path, 'r') as f:
        for line in f:
            path, size, mtime = line.strip().split('|')
            data[path] = (int(size), int(mtime))
    return data


def format_size(size):
    for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} ТБ"


def main(snapshot_a_path, snapshot_b_path):
    snapshot_a = read_snapshot(snapshot_a_path)
    snapshot_b = read_snapshot(snapshot_b_path)

    changed_files = []
    new_files = []
    only_in_a = []

    all_paths = set(snapshot_a) | set(snapshot_b)

    for path in all_paths:
        a = snapshot_a.get(path)
        b = snapshot_b.get(path)

        if a and b:
            if a != b:
                changed_files.append((path, b[0]))
        elif b:
            new_files.append((path, b[0]))
        elif a:
            only_in_a.append((path, a[0]))

    print("✏️ ЗМІНЕНІ ФАЙЛИ:")
    for path, size in changed_files:
        print(f"{path} ({format_size(size)})")

    print("\n🆕 НОВІ ФАЙЛИ (лише в другому снепшоті):")
    for path, size in new_files:
        print(f"{path} ({format_size(size)})")

    print("\n❌ ФАЙЛИ, ЩО БУЛИ ЛИШЕ В ПЕРШОМУ СНЕПШОТІ:")
    for path, size in only_in_a:
        print(f"{path} ({format_size(size)})")

    # 📊 Сводка
    count_changed = len(changed_files)
    size_changed = sum(size for _, size in changed_files)

    count_new = len(new_files)
    size_new = sum(size for _, size in new_files)

    count_removed = len(only_in_a)
    size_removed = sum(size for _, size in only_in_a)

    print("\n📊 СВОДКА:")
    print(f"✏️ Змінено файлів: {count_changed} (загалом {format_size(size_changed)})")
    print(f"🆕 Додано нових файлів: {count_new} (загалом {format_size(size_new)})")
    print(f"🗑️ Видалено файлів: {count_removed} (загалом {format_size(size_removed)})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Порівняння двох снепшотів каталогу")
    parser.add_argument("-a", "--snapshot-a", required=True, help="Файл першого снепшоту (ЧасА)")
    parser.add_argument("-b", "--snapshot-b", required=True, help="Файл другого снепшоту (ЧасБ)")
    args = parser.parse_args()

    main(args.snapshot_a, args.snapshot_b)
