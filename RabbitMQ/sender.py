#!/usr/bin/env python
from random import randint

import pika

QUEUE_NAME = 'test'

credentials = pika.PlainCredentials("test", "test")
params = pika.ConnectionParameters(host='127.0.0.1', port=5672, credentials=credentials)
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue=QUEUE_NAME, durable=True)

message = 'Hello World!'+'.'*randint(2, 10)
channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message,
                      properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
print(f" 📨 Sent '{message}'")
connection.close()
