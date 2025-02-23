#!/usr/bin/env python
from random import randint
import ssl
import socket
from dotenv import load_dotenv
import pika
import os

# Завантаження змінних з файлу .env
load_dotenv()

QUEUE_NAME = 'test'
HOST = os.getenv('REMOTE_HOST', '127.0.0.1')
SERVER_HOSTNAME = os.getenv('SERVER_HOSTNAME', socket.gethostname())
PORT = int(os.getenv('PORT', '5671'))

# Налаштування SSL
context = ssl.create_default_context(cafile="./testca/ca_certificate.pem")
context.load_cert_chain(certfile="./client/client_certificate.pem", keyfile="./client/private_key.pem")

credentials = pika.PlainCredentials("test", "test")
# Тут в якості server_hostname необхідно використати вивід команди hostname
params = pika.ConnectionParameters(
    host=HOST,
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
