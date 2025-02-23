# Приклад роботи з RabbitMQ

## Установка та запуск

### За допомогою **apt**

Для установки виконайте наступні команди:

```bash
sudo apt update
sudo apt install rabbitmq-server
# Перед запуском додайте необхідні файли конфігурації та сертифікати (див. далі)
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# Перевірка статуса
sudo systemctl status rabbitmq-server

# RabbitMQ comes with a web-based management interface that makes it easier to monitor and manage your RabbitMQ server. To enable this plugin, run the following commands:
sudo rabbitmq-plugins enable rabbitmq_management
sudo systemctl restart rabbitmq-server
# If you enabled the RabbitMQ management plugin, you can access the web interface by opening your web browser and navigating to the following [URL](http://localhost:15672/)
```

При встановленні з **apt** сервер автоматично запускається, тому змінити `default_user` та `default_pass` не вийде, тому треба додати нового користувача та видалити користувача **guest**:

```bash
sudo rabbitmqctl add_user 'test' 'test'
sudo rabbitmqctl set_user_tags test administrator
sudo rabbitmqctl list_users
sudo rabbitmqctl set_permissions -p / test ".*" ".*" ".*"
sudo rabbitmqctl delete_user 'guest'

```

### Використання **Docker**

- Скопіюйте файл **docker_run.sh** в файл **local.docker_run.sh**
- Замініть в новому файлі:

  - <your_user> на логін для свого користувача по замовчанню, який можна згенерувати за допомогою:
  - <your_password> на пароль свого користувача по замовчанню, який можна згенерувати за допомогою:

## Генерація сертифікатів TLS

### Рекомендований спосіб

Порядок ручної генерації сертифікатів описано на [відповідній сторінці](https://www.rabbitmq.com/docs/ssl#manual-certificate-generation) документації. Крім того, для генерації можна використовувати [автоматичний спосіб](https://www.rabbitmq.com/docs/ssl#automated-certificate-generation) за допомогою [tls-gen](https://github.com/rabbitmq/tls-gen).

Для зручності при створенні сертифікатів можна використовувати скрипти **cert.XX.init.sh**.

В файлі **cert.00.init.sh** при генерації openssl.cnf можна додати в кінець:

```ini
subjectAltName = @alt_names

[ alt_names ]
IP.1 = 127.0.0.1
# Тут замість 127.0.0.1 можна додати ip-адресу Вашого серверу
```

Після цього можна буде використати для з'єднання:

```python
params = pika.ConnectionParameters(
    host='127.0.0.1',
    port=5671,
    credentials=credentials,
    ssl_options=pika.SSLOptions(context)
)
```

Інакше треба при з'єднанні обов'язково вказувати при з'єднанні назву хоста, для якого генерувався сертифікат:

```python
params = pika.ConnectionParameters(
    host='127.0.0.1',
    port=5671,
    credentials=credentials,
    ssl_options=pika.SSLOptions(context, server_hostname='<your_hostname>')
)
```

### Простий спосіб (не певен, що найкращій)

Створимо **кореневий сертифікат (CA)** та підпишемо серверні і клієнтські сертифікати.

```sh
mkdir -p certs && cd certs

# 1. Створюємо кореневий сертифікат (CA)
openssl req -x509 -new -nodes -keyout ca.key -out ca.crt -days 3650 -subj "/CN=MyCA"

# 2. Генеруємо ключ для сервера
openssl genpkey -algorithm RSA -out server.key

# 3. Запит на підпис (CSR) для сервера
openssl req -new -key server.key -out server.csr -subj "/CN=rabbitmq"

# 4. Підписуємо серверний сертифікат кореневим CA
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 3650
```

Тепер створимо клієнтський сертифікат:

```sh
openssl genpkey -algorithm RSA -out client.key
openssl req -new -key client.key -out client.csr -subj "/CN=client"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 3650
```

Тепер у нас є файли:

- `ca.crt` (кореневий сертифікат)
- `server.crt`, `server.key` (серверний сертифікат)
- `client.crt`, `client.key` (клієнтський сертифікат)

### TLS Certificate and Private Key Rotation

This description has taken from [official documentation](https://www.rabbitmq.com/docs/ssl#rotation).

Server TLS certificates (public keys) and private keys have expiration dates and will need to be replaced (rotated) every so often.

The replacement process involves the following steps:

- Replace the files on disk
- Clear the certificate and private key store cache on the node

Without the second step, the new certificate/key pair will be used by the node after a period of time, as the TLS implementation in the runtimes purges its certificate store cache.

#### Replacing Certificate and Private Key Files on Disk

Simply replace the server certificate, server private key and (if needed) the certificate authority bundle files with their new versions.

#### Clearing the Certificate and Private Key Store Cache

```bash
rabbitmqctl eval -n [target-node@hostname] 'ssl:clear_pem_cache().'
```

## Налаштування

### Копіювання сертифікатів

Створіть у каталозі **/etc/rabbitmq** підкаталог **tls**, у якому зберігатимуться сертифікати сервера, і змініть його власника:

```bash
mkdir -p /etc/rabbitmq/tls
chown rabbitmq:rabbitmq /etc/rabbitmq/tls
```

Скопіюйте до каталогу **/etc/rabbitmq/tls** файли сертифікатів, створені раніше:

- **./testca/ca_certificate.pem** — сертифікат центру сертифікації (CA);
- **./server/server_certificate.pem** — сертифікат сервера RabbitMQ;
- **./server/private_key.pem** — приватний ключ сервера.

Після копіювання _ОБОВ'ЯЗКОВО_ змініть власника цих файлів, оскільки сервер не запуститься, якщо файл **private_key.pem** матиме некоректні права доступу:

```bash
chown rabbitmq:rabbitmq /etc/rabbitmq/tls/*
chmod 600 /etc/rabbitmq/tls/private_key.pem
```

Також переконайтеся, що каталог **tls** має правильні права доступу:

```bash
chmod 750 /etc/rabbitmq/tls
```

Ці налаштування забезпечать безпечне зберігання сертифікатів і правильну роботу RabbitMQ.

### Налаштування файлу конфігурації **rabbitmq.conf**

Файл **rabbitmq.conf** містить рекомендовані налаштування.

Якщо інсталяція виконана за допомогою **apt**, скопіюйте цей файл в каталог **/etc/rabbitmq/rabbitmq.conf** та відредагуйте його для своїх потреб. Обов'язково змініть значення налаштувань `default_user `, та `default_pass`!

Крім того, можна змінити власника для файлу налаштувань:

```bash
pwd
# /etc/rabbitmq
chown rabbitmq:rabbitmq rabbitmq.conf
```

Якщо використовується **Docker**, то скопіюйте файл конфігурації **rabbitmq.conf** в файл **local.rabbitmq.conf** та зробіть відповідні правки в **local.docker_run.sh**.

### Змінні середовища

Для налаштування параметрів сервера, на якому запущено RabbitMQ, можна використовувати такі змінні середовища:

- **REMOTE_HOST** — IP-адреса або доменне ім'я сервера (за замовчуванням `"127.0.0.1"`).
- **SERVER_HOSTNAME** — хостове ім'я, для якого було згенеровано сертифікати сервера та клієнта (за замовчуванням визначається через `socket.gethostname()`).
- **PORT** — порт, на якому працює RabbitMQ (за замовчуванням `5671`).

Щоб задати власні значення цих змінних середовища, скопіюйте файл **dot.env** у **.env** і вкажіть необхідні параметри. Вони будуть використані під час запуску скриптів.

Якщо RabbitMQ запущено на віддаленому сервері, переконайтеся, що клієнт використовує відповідні сертифікати, згенеровані на цьому сервері. Без них клієнт не зможе встановити безпечне з'єднання.

## Примітки

### Генерація логіна та пароля

Логін можна згенерувати наступною командою:

```bash
openssl rand -base64 16 | tr -d '/+='
```

Пароль можна згенерувати наступною командою (деякі символи не використовуються, щоб не перейматись щодо їх екранування):

```bash
apg -a 1 -n 1 -m 32 -E "#'\"\`$\&"
```

Для генерації логіна та пароля також можна використати UUID:

```bash
uuidgen | tr '[:upper:]' '[:lower:]'
```
