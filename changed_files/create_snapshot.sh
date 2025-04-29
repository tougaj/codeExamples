#!/usr/bin/env bash

# Ініціалізація змінних
DIR=""
OUT=""

# Обробка аргументів
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -d|--dir)
            DIR="$2"
            shift 2
            ;;
        -o|--out)
            OUT="$2"
            shift 2
            ;;
        -*)
            echo "❌ Невідомий параметр: $1" >&2
            exit 1
            ;;
        *)
            echo "❌ Неочікуване значення: $1" >&2
            exit 1
            ;;
    esac
done

# Перевірка обов'язкових параметрів
if [[ -z "$DIR" || -z "$OUT" ]]; then
    echo "❌ Використання: $0 -d /шлях/до/каталогу -o snapshot.txt" >&2
    echo "   або: $0 --dir /шлях/до/каталогу --out snapshot.txt" >&2
    exit 1
fi

# Зняття снепшоту
find "$DIR" -type f -exec stat --format="%n|%s|%Y" {} \; > "$OUT"

echo "✅ Снепшот збережено до $OUT"
