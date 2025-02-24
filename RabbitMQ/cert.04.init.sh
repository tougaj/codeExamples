#!/usr/bin/env bash

# Копіювання сертифікатів у відповідний каталог серверу та налаштування прав доступу до файлів
# !!! Даний скрипт має запускатись з правами sudo !!!

# Встановлення каталогу для сертифікатів
TLS_DIR="/etc/rabbitmq/tls"

# Створення каталогу, якщо його не існує
echo "📁 Створюю каталог $TLS_DIR..."
mkdir -p "$TLS_DIR"

# Зміна власника каталогу
echo "🔑 Змінюю власника каталогу $TLS_DIR..."
chown rabbitmq:rabbitmq "$TLS_DIR"

# Копіювання файлів сертифікатів
echo "📄 Копіюю сертифікати..."
cp ./testca/ca_certificate.pem "$TLS_DIR"
cp ./server/server_certificate.pem "$TLS_DIR"
cp ./server/private_key.pem "$TLS_DIR"

# Зміна власника файлів
echo "🛠️ Змінюю власника файлів..."
chown rabbitmq:rabbitmq "$TLS_DIR"/*

# Встановлення правильних прав доступу
echo "🔒 Налаштовую права доступу..."
chmod 600 "$TLS_DIR/private_key.pem"
chmod 640 "$TLS_DIR/ca_certificate.pem" "$TLS_DIR/server_certificate.pem"
chmod 750 "$TLS_DIR"

echo "✅ Готово! Сертифікати скопійовані та налаштовані."
