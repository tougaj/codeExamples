#!/usr/bin/env python
import os
import time

import pika

QUEUE_NAME = 'test'


def main():
    credentials = pika.PlainCredentials("test", "test")
    params = pika.ConnectionParameters(host='127.0.0.1', port=5672, credentials=credentials)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}")
        time.sleep(body.count(b'.'))
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        connection.close()  # закриваємо з'єднання після завершення
        print('Connection closed')


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        os._exit(0)
