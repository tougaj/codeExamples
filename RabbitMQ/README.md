# Приклад роботи з RabbitMQ

## Генерація сертифікатів TLS

### Простий спосіб

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

## Налаштування файлу конфігурації **rabbitmq.conf**

Файл **rabbitmq.conf** містить рекомендовані налаштування

## Налаштування контейнера

- Скопіюйте файл **docker_run.sh** в файл **local.docker_run.sh**
- Замініть в новому файлі:

	+ <your_user> на логін для свого користувача по замовчанню, який можна згенерувати за допомогою:
	```bash
	openssl rand -base64 16 | tr -d '/+='
	```
	+ <your_password> на пароль свого користувача по замовчанню, який можна згеренувати за допомогою:
	```bash
	apg -a 1 -n 1 -m 32 -E "#'\"\`$"
	# Деякі символи не використовуються, щоб не перйматись щодо їх екранування
	```

> Для логіна та пароля також можна використати:
> ```bash
> uuidgen | tr '[:upper:]' '[:lower:]'
> ```
