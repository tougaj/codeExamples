#!/usr/bin/env bash

# docker pull qdrant/qdrant

# Якщо Вам потрібно, щоб цей контейнер автоматично запускався завжди,
# додайте до команди запуску "--restart always"
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant

# Для зупинка даного контейнера використовуйте
# docker stop qdrant
