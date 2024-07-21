# docker

Для збірки контейнеру використовуйте наступну команду:


```bash
docker build -t deepface:latest .

```

Для запуску контейнеру, який містить налаштоване середовище для роботи з deepFace, використовуйте наступну команду:


```bash
docker run -it --rm -v $PWD:/app/deepface deepface:latest bash

```
