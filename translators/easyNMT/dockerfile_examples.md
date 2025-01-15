Ось два приклади `Dockerfile`: один для середовища з CPU, а інший для середовища з GPU. 

---

### **1. Dockerfile для CPU**
```dockerfile
# Використовуємо офіційний Python образ
FROM python:3.9-slim

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо залежності для Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копіюємо код програми
COPY . /app
WORKDIR /app

# Відкриваємо порт для API
EXPOSE 8000

# Команда для запуску сервісу
CMD ["uvicorn", "translation_service:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **`requirements.txt` для CPU:**
```plaintext
fastapi
uvicorn
easynmt
```

---

### **2. Dockerfile для GPU**
```dockerfile
# Використовуємо базовий образ NVIDIA з підтримкою CUDA
FROM nvidia/cuda:11.8.0-base-ubuntu20.04

# Встановлюємо Python та системні залежності
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо Python-залежності
COPY requirements-gpu.txt /app/requirements-gpu.txt
RUN python3 -m pip install --no-cache-dir -r /app/requirements-gpu.txt

# Копіюємо код програми
COPY . /app
WORKDIR /app

# Відкриваємо порт для API
EXPOSE 8000

# Команда для запуску сервісу
CMD ["uvicorn", "translation_service:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **`requirements-gpu.txt` для GPU:**
```plaintext
fastapi
uvicorn
easynmt
torch==2.0.0+cu118 -f https://download.pytorch.org/whl/torch_stable.html
```

---

### **Додаткові дії після створення Dockerfile**
1. **Створення образу для CPU**:
   ```bash
   docker build -t translation-service-cpu -f Dockerfile.cpu .
   ```

2. **Створення образу для GPU**:
   ```bash
   docker build -t translation-service-gpu -f Dockerfile.gpu .
   ```

3. **Запуск контейнера**:
   - **CPU**:
     ```bash
     docker run -d -p 8000:8000 translation-service-cpu
     ```
   - **GPU** (з підключенням GPU через Docker):
     ```bash
     docker run --gpus all -d -p 8000:8000 translation-service-gpu
     ```

---

Ці `Dockerfile` забезпечують належну роботу сервісу як у середовищі CPU, так і GPU.
