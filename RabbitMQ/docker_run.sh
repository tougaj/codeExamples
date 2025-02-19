#!/usr/bin/env bash

# З використанням TLS та аутентифікацією за допомогою користувача за замовчанням
docker run -d --rm --name rabbitmq \
	-p 5671:5671 -p 15672:15672 \
	-e RABBITMQ_DEFAULT_USER="<your_user>" \
	-e RABBITMQ_DEFAULT_PASS="<your_password>" \
	-v $PWD/certs:/etc/rabbitmq/ssl \
	-v $PWD/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf \
	rabbitmq:4-management