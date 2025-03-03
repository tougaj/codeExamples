#!/usr/bin/env python
import os
import socket
import ssl
from pathlib import Path
from random import randint

import pika
from dotenv import load_dotenv

# Завантаження змінних з файлу .env
load_dotenv()

QUEUE_NAME = 'test'
HOST = os.getenv('REMOTE_HOST', '127.0.0.1')
SERVER_HOSTNAME = os.getenv('SERVER_HOSTNAME', socket.gethostname())
PORT = int(os.getenv('PORT', '5671'))
CERTIFICATES_ROOT_PATH = Path(os.getenv('CERTIFICATES_ROOT_PATH', './'))
USER_LOGIN = os.getenv("USER_LOGIN", "test")
USER_PASSWORD = os.getenv("USER_PASSWORD", "test")

# Налаштування SSL
context = ssl.create_default_context(cafile=CERTIFICATES_ROOT_PATH / "testca/ca_certificate.pem")
context.load_cert_chain(certfile=CERTIFICATES_ROOT_PATH / "client/client_certificate.pem", keyfile=CERTIFICATES_ROOT_PATH / "client/private_key.pem")

credentials = pika.PlainCredentials(USER_LOGIN, USER_PASSWORD)
# Тут в якості server_hostname необхідно використати вивід команди hostname
params = pika.ConnectionParameters(
    host=HOST,
    virtual_host='/',
    port=PORT,
    credentials=credentials,
    ssl_options=pika.SSLOptions(context, server_hostname=SERVER_HOSTNAME)
)
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue=QUEUE_NAME, durable=True)

message = 'Hello World!'+'.'*randint(2, 10)
channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message,
                      properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
print(f" 📨 Sent '{message}'")
connection.close()
