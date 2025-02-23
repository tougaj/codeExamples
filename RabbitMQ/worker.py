#!/usr/bin/env python
import os
import socket
import ssl
import time

import pika
from dotenv import load_dotenv

# Завантаження змінних з файлу .env
load_dotenv()

QUEUE_NAME = 'test'
HOST = os.getenv('REMOTE_HOST', '127.0.0.1')
SERVER_HOSTNAME = os.getenv('SERVER_HOSTNAME', socket.gethostname())
PORT = int(os.getenv('PORT', '5671'))


def main():
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
    print(' 📩 Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(f" 📨 Received '{body.decode()}'")
        time.sleep(body.count(b'.'))
        print(" ✅ Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print('⛔ Interrupted')
    finally:
        connection.close()  # закриваємо з'єднання після завершення
        print('🔒 Connection closed')


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        os._exit(0)
