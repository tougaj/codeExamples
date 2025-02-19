Якщо хочеш підключитися до RabbitMQ з **аутентифікацією через логін/пароль** + **TLS (SSL)**, то потрібно:  

1. **Налаштувати RabbitMQ на використання TLS**  
2. **Створити сертифікати для сервера та клієнта**  
3. **Запустити RabbitMQ через Docker**  
4. **Налаштувати Python-клієнт для підключення через TLS**

---

## 🔹 1. Генерація сертифікатів TLS  

Створимо **кореневий сертифікат (CA)** та підпишемо серверні і клієнтські сертифікати.  

```sh
mkdir -p certs && cd certs

# 1. Створюємо кореневий сертифікат (CA)
openssl req -x509 -new -nodes -keyout ca.key -out ca.crt -days 365 -subj "/CN=MyCA"

# 2. Генеруємо ключ для сервера
openssl genpkey -algorithm RSA -out server.key

# 3. Запит на підпис (CSR) для сервера
openssl req -new -key server.key -out server.csr -subj "/CN=rabbitmq"

# 4. Підписуємо серверний сертифікат кореневим CA
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365
```

Тепер створимо клієнтський сертифікат:

```sh
openssl genpkey -algorithm RSA -out client.key
openssl req -new -key client.key -out client.csr -subj "/CN=client"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365
```

Тепер у нас є файли:  
- `ca.crt` (кореневий сертифікат)  
- `server.crt`, `server.key` (серверний сертифікат)  
- `client.crt`, `client.key` (клієнтський сертифікат)  

---

## 🔹 2. Налаштування RabbitMQ для TLS  

Створимо конфігураційний файл **`rabbitmq.conf`**:  

```ini
# Відключаємо звичайний порт, включаємо TLS
listeners.tcp = none
listeners.ssl.default = 5671

# Включаємо TLS
ssl_options.cacertfile = /etc/rabbitmq/ssl/ca.crt
ssl_options.certfile   = /etc/rabbitmq/ssl/server.crt
ssl_options.keyfile    = /etc/rabbitmq/ssl/server.key

# Верифікація клієнтського сертифіката (опціонально)
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = true
```

---

## 🔹 3. Запуск RabbitMQ через Docker  

Копіюємо сертифікати в папку `certs/` та запускаємо контейнер:

```sh
docker run -d --name rabbitmq \
  -p 5671:5671 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=myuser \
  -e RABBITMQ_DEFAULT_PASS=mypassword \
  -v $PWD/certs:/etc/rabbitmq/ssl \
  -v $PWD/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf \
  rabbitmq:3-management
```

Переконайся, що RabbitMQ працює:

```sh
docker logs rabbitmq | grep "TLS"
```

---

## 🔹 4. Python-клієнт із TLS та логіном/паролем  

### 🔹 Встановлення бібліотеки  
```sh
pip install pika
```

### 🔹 Python-код для підключення  

```python
import pika
import ssl

# Налаштування SSL
context = ssl.create_default_context(cafile="certs/ca.crt")
context.load_cert_chain(certfile="certs/client.crt", keyfile="certs/client.key")

# Налаштування з'єднання
credentials = pika.PlainCredentials("myuser", "mypassword")
params = pika.ConnectionParameters(
    host="your_server_ip",
    port=5671,
    credentials=credentials,
    ssl_options=pika.SSLOptions(context)
)

# Підключення
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue="test")

print("Connected to RabbitMQ with TLS and authentication!")
channel.basic_publish(exchange="", routing_key="test", body="Hello TLS!")
connection.close()
```

---

## 🔹 5. Перевірка роботи  
1. Переконайся, що RabbitMQ слухає порт **5671**:  
   ```sh
   docker logs rabbitmq | grep "TLS"
   ```
2. Запусти Python-клієнт:  
   ```sh
   python client.py
   ```
3. Перевір, чи повідомлення з'явилося у RabbitMQ (в Web UI `http://your_server_ip:15672/` → Queues → `test`).

---

## 🔹 Висновок  
✅ RabbitMQ працює **з TLS**  
✅ Клієнт підключається **з шифруванням**  
✅ Використовується **логін та пароль** для автентифікації  

Якщо потрібне **примусове використання клієнтського сертифіката** або інтеграція з **OAuth2 + TLS**, скажи – поясню далі 🚀


Щоб налаштувати **TLS-аутентифікацію без логіна та пароля**, потрібно виконати такі кроки:  

1. Змінити конфігурацію RabbitMQ, щоб він аутентифікував клієнтів через **сертифікати**  
2. Згенерувати унікальні **сертифікати клієнтів**  
3. Підключитися до RabbitMQ без логіна та пароля, використовуючи **сертифікати**  

---

# 🔹 1. Налаштування RabbitMQ для аутентифікації через TLS  

Створи або відредагуй файл **`rabbitmq.conf`**:  

```ini
# Вимкнути звичайні TCP-з'єднання (необов'язково, але підвищує безпеку)
listeners.tcp = none
listeners.ssl.default = 5671

# Шлях до сертифікатів
ssl_options.cacertfile = /etc/rabbitmq/ssl/ca.crt
ssl_options.certfile   = /etc/rabbitmq/ssl/server.crt
ssl_options.keyfile    = /etc/rabbitmq/ssl/server.key

# Включаємо перевірку клієнтських сертифікатів
ssl_options.verify     = verify_peer
ssl_options.fail_if_no_peer_cert = true

# Вимкнути автентифікацію за паролем, залишити тільки TLS
auth_mechanisms.1 = external
```

> **`auth_mechanisms.1 = external`** — означає, що RabbitMQ використовуватиме **сертифікати клієнтів** замість логіна/пароля.

### 🔹 2. Перезапуск RabbitMQ  
Якщо RabbitMQ працює в Docker, виконай команду:  

```sh
docker restart rabbitmq
```

---

# 🔹 3. Генерація унікальних клієнтських сертифікатів  

Якщо ти вже маєш **CA (кореневий сертифікат)**, то можеш згенерувати **окремі сертифікати для кожного клієнта**:

```sh
cd certs

# 1. Генеруємо ключ для клієнта
openssl genpkey -algorithm RSA -out client.key

# 2. Створюємо запит на підпис (CSR)
openssl req -new -key client.key -out client.csr -subj "/CN=client"

# 3. Підписуємо клієнтський сертифікат нашим CA
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365
```

Після цього у клієнта будуть файли:  
- `client.crt` (сертифікат клієнта)  
- `client.key` (приватний ключ клієнта)  
- `ca.crt` (кореневий сертифікат CA)  

Ці файли потрібно передати **на клієнтський пристрій**.

---

# 🔹 4. Підключення клієнта без логіна та пароля  

У **Python** можна використовувати **pika** для підключення до RabbitMQ через TLS-аутентифікацію:

```python
import pika
import ssl

# Налаштування TLS
context = ssl.create_default_context(cafile="/path/to/certs/ca.crt")
context.load_cert_chain(certfile="/path/to/certs/client.crt", keyfile="/path/to/certs/client.key")

# Параметри підключення (без логіна та пароля)
params = pika.ConnectionParameters(
    host="your_server_ip",
    port=5671,
    ssl_options=pika.SSLOptions(context)
)

# Встановлюємо з'єднання
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue="test")

print("✅ Підключено до RabbitMQ через TLS-аутентифікацію!")
channel.basic_publish(exchange="", routing_key="test", body="Hello via TLS Auth!")
connection.close()
```

---

# 🔹 5. Перевірка підключення  

Щоб перевірити, що клієнт дійсно **автентифікується через сертифікати**, подивись **логи RabbitMQ**:  

```sh
docker logs rabbitmq | grep "TLS"
```

У логах має бути щось подібне:  
```
TLS connection from 192.168.1.100:12345 accepted
```

---

# 🔹 6. Як контролювати доступ клієнтів?  

### 📌 Спосіб 1: Контроль через **CN (Common Name)** у сертифікатах  
RabbitMQ використовує **CN (Common Name)** з клієнтського сертифіката як ім'я користувача.  
Тобто, якщо клієнтський сертифікат має:  

```sh
openssl req -new -key client.key -out client.csr -subj "/CN=client1"
```

То RabbitMQ створить користувача `client1`.  
> Якщо треба дати йому доступ до черг, використовуй **policies** та **permissions**.

### 📌 Спосіб 2: Використання **Subject Alternative Name (SAN)**  
Можна додати конкретні імена в сертифікати, щоб RabbitMQ міг легко їх ідентифікувати.

---

# 🔹 7. Чи можна підключати кілька клієнтів?
Так! Просто **згенеруй нові сертифікати** для кожного клієнта (наприклад, `client2.crt`, `client2.key`) та передай їх.

---

# ✅ Висновок  
✔ Тепер RabbitMQ **автентифікує клієнтів** через TLS-сертифікати без логіна та пароля.  
✔ Кожен клієнт може мати **свій власний сертифікат**.  
✔ Це значно **безпечніше**, ніж використання паролів.  

Якщо є питання – питай! 🚀🔒


Коли RabbitMQ використовує **TLS-аутентифікацію**, він автоматично бере ім'я користувача з **CN (Common Name)** сертифіката клієнта. Але **саме по собі це не дає прав доступу до черг**.  

Щоб клієнт міг **читати та писати в черги**, потрібно **видати йому відповідні права доступу**.

---

# 🔹 1. Додання клієнта як користувача  
Припустимо, що сертифікат клієнта містить:  

```sh
openssl req -new -key client.key -out client.csr -subj "/CN=client1"
```

Це означає, що RabbitMQ сприйматиме цього клієнта як користувача `client1`.  
Але **за замовчуванням у нього немає жодних прав**.  

Щоб видати йому права, виконай команду на сервері RabbitMQ:

```sh
docker exec -it rabbitmq rabbitmqctl add_user client1 ""
docker exec -it rabbitmq rabbitmqctl set_user_tags client1 administrator
```

> **Примітка:**  
> Якщо RabbitMQ використовує тільки **TLS-аутентифікацію** (`auth_mechanisms.1 = external`), то пароль для користувача `client1` не використовується (його можна залишити пустим).

---

# 🔹 2. Дозвіл на доступ до всіх черг  
Тепер треба дозволити `client1` доступ до всіх черг та обмінників:

```sh
docker exec -it rabbitmq rabbitmqctl set_permissions -p / client1 ".*" ".*" ".*"
```

Це означає:  
- **"read" (читай):** `.*` – клієнт може читати всі черги  
- **"write" (пиши):** `.*` – клієнт може писати в усі черги  
- **"configure" (конфігурація):** `.*` – клієнт може створювати черги  

Тепер `client1` може взаємодіяти з RabbitMQ через **сертифікати** без пароля.

---

# 🔹 3. Обмеження доступу до конкретних черг  
Щоб дати доступ тільки до **певної черги**, замість `.*` вкажи її назву:  

```sh
docker exec -it rabbitmq rabbitmqctl set_permissions -p / client1 "^my_queue$" "^my_queue$" "^my_queue$"
```

Тепер `client1` може працювати тільки з **чергою `my_queue`**, але не з іншими.

---

# 🔹 4. Використання політик (policies)  
Політики в RabbitMQ дозволяють керувати параметрами черг, наприклад:
- TTL повідомлень
- Максимальний розмір черги
- Дублікація повідомлень між нодами

Щоб встановити політику для всіх черг, що починаються на `"logs_"`, виконай:

```sh
docker exec -it rabbitmq rabbitmqctl set_policy my_policy "^logs_.*" '{"max-length":10}' --apply-to queues
```

Це означає:
- Всі черги, що починаються на `"logs_"`, зможуть містити **не більше 10 повідомлень**  
- Політика застосовується **до всіх черг (`--apply-to queues`)**  

---

# 🔹 5. Перевірка прав клієнта  
Щоб перевірити, які права має клієнт, запусти:

```sh
docker exec -it rabbitmq rabbitmqctl list_user_permissions client1
```

Отримаєш щось на зразок:

```
/  ^my_queue$  ^my_queue$  ^my_queue$
```

Це означає, що `client1` може працювати тільки з `my_queue`.

---

# ✅ Висновок  
- **RabbitMQ автоматично розпізнає ім'я клієнта** через **CN у сертифікаті**  
- **Але доступ до черг потрібно вручну налаштувати через `set_permissions`**  
- **Можна обмежити доступ до певних черг** або **застосовувати політики**  

Тепер твій RabbitMQ захищений та налаштований! 🔒🚀