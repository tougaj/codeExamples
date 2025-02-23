#!/usr/bin/env python
from random import randint
import ssl
import socket

import pika

QUEUE_NAME = 'test'

# Налаштування SSL
context = ssl.create_default_context(cafile="./testca/ca_certificate.pem")
context.load_cert_chain(certfile="./client/client_certificate.pem", keyfile="./client/private_key.pem")

credentials = pika.PlainCredentials("test", "test")
# Тут в якості server_hostname необхідно використати вивід команди hostname
hostname = socket.gethostname()
params = pika.ConnectionParameters(
    host='127.0.0.1',
    port=5671,
    credentials=credentials,
    ssl_options=pika.SSLOptions(context, server_hostname=hostname)
)
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue=QUEUE_NAME, durable=True)

message = 'Hello World!'+'.'*randint(2, 10)
channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message,
                      properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
print(f" 📨 Sent '{message}'")
connection.close()
