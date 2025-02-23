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

## Налаштування

### Копіювання сертифікатів

Створіть в каталозі **/etc/rabbitmq** каталог **tls**, в якому будуть зберігатись сертифікати сервера, та змініть його власника:

```bash
pwd
# /etc/rabbitmq
mkdir tls
chown rabbitmq:rabbitmq tls
```

Скопіюйте в новостворений каталог **/etc/rabbitmq/tls** файли сертифікатів, створених вище:

- **./testca/ca_certificate.pem**;
- **./server/server_certificate.pem**;
- **./server/private_key.pem**.

Після цього _ОБОВ'ЯЗКОВО_ змініть власника скопійованих файлів (в іншому випадку сервер не запуститься, тому що файл **private_key.pem** має специфічні права доступу):

```bash
pwd
# /etc/rabbitmq/tls
chown rabbitmq:rabbitmq *
```

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
