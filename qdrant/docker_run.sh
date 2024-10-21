#!/usr/bin/env bash

# docker pull qdrant/qdrant

# Якщо Вам потрібно, щоб цей контейнер автоматично запускався завжди,
# додайте до команди запуску "--restart always", або  "--restart unless-stopped"
# 
# З довідки (https://docs.docker.com/engine/containers/start-containers-automatically/):
# always        	Always restart the container if it stops. If it's manually stopped, 
#                   it's restarted only when Docker daemon restarts or the container itself
#                   is manually restarted. (See the second bullet listed in restart policy details)
# unless-stopped	Similar to always, except that when the container is stopped 
#                   (manually or otherwise), it isn't restarted even after Docker daemon restarts.
#
# Крім того, якщо Ви хочете, щоб контейнер автоматично видалявся після остановки,
# додайте до команди запуску "--rm"

docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant

# Якщо Ви використовуєте "--name qdrant", то в подальшому запускати контейнер
# можна за допомогою команди:
# docker start qdrant
#
# Видалити контейнер можна командою:
# docker rm qdrant
#
# Переглянути список всіх контейнерів можнна командою:
# docker ps -a

# Для зупинка даного контейнера використовуйте наступну команду:
# docker stop qdrant

