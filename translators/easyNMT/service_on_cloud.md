## Щоб розгорнути [EasyNMT](https://github.com/UKPLab/EasyNMT) на хмарному сервісі для перекладу текстів, потрібно виконати кілька етапів:

---

### 1. **Вибір хмарного сервісу**
Обери хмарну платформу, наприклад:
- **AWS (Amazon Web Services)**: EC2 або Lambda.
- **Google Cloud**: Compute Engine або Cloud Run.
- **Microsoft Azure**: Virtual Machines або Azure Functions.
- **Heroku**: простий у використанні для невеликих проєктів.

---

### 2. **Налаштування середовища**
#### 2.1. Вибір потужності
Обери сервер із достатньою кількістю пам'яті, залежно від обсягу тексту, що перекладатиметься. GPU може суттєво прискорити роботу, особливо якщо працюєш з великими моделями.

#### 2.2. Операційна система
Рекомендується використовувати Ubuntu (наприклад, 20.04 або 22.04).

#### 2.3. Інсталяція Python
Встанови Python 3.8 або новішу версію. Наприклад:
```bash
sudo apt update
sudo apt install python3 python3-pip -y
```

---

### 3. **Інсталяція EasyNMT**
#### 3.1. Клонування репозиторію
```bash
git clone https://github.com/UKPLab/EasyNMT.git
cd EasyNMT
```

#### 3.2. Встановлення залежностей
Використовуй `pip` для встановлення пакету:
```bash
pip3 install easynmt
```

---

### 4. **Створення API для перекладу**
Щоб надати доступ до перекладу через HTTP-запити, створимо простий веб-сервер, наприклад, за допомогою FastAPI:

#### `main.py`
```python
from fastapi import FastAPI, Request
from pydantic import BaseModel
from easynmt import EasyNMT

app = FastAPI()
model = EasyNMT('opus-mt')  # Вибери модель, яка тобі підходить

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

@app.post("/translate/")
async def translate(request: TranslationRequest):
    translated_text = model.translate(
        request.text, 
        source_lang=request.source_lang, 
        target_lang=request.target_lang
    )
    return {"translated_text": translated_text}
```

#### Встановлення FastAPI та uvicorn:
```bash
pip3 install fastapi uvicorn
```

---

### 5. **Розгортання**
#### 5.1. Локальний запуск
Перевір роботу локально:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 5.2. Контейнеризація (опціонально)
Можна створити Docker-образ для розгортання:

**Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Створи `requirements.txt` із вмістом:
```
fastapi
uvicorn
easynmt
```

Далі збери та запусти контейнер:
```bash
docker build -t easynmt-service .
docker run -p 8000:8000 easynmt-service
```

#### 5.3. Розгортання на хмарі
- На AWS EC2 або GCP Compute Engine просто запусти сервер із кодом.
- Для Heroku додай `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```
І розгорни проєкт через `git push`.

---

### 6. **Тестування API**
Використовуй `curl` або Postman для тестування:
```bash
curl -X POST "http://<SERVER_IP>:8000/translate/" \
-H "Content-Type: application/json" \
-d '{"text": "Hello, world!", "source_lang": "en", "target_lang": "uk"}'
```

---

### 7. **Оптимізація**
- Використовуй GPU для прискорення.
- Налаштуй автоскейлінг або кешування для частих запитів (наприклад, Redis).
- Забезпеч безпеку API (додай аутентифікацію).

--- 

У результаті, ти матимеш розгорнутий сервіс для перекладу текстів із використанням EasyNMT.

---

## Пункт **5.3. Розгортання на хмарі** передбачає налаштування твого сервісу на конкретній хмарній платформі, наприклад AWS, Google Cloud або Heroku. Ось покроковий детальний опис для кожного з цих варіантів.

---

### **1. AWS EC2**
Amazon EC2 дозволяє створити віртуальний сервер (інстанс) для розгортання сервісу.

#### Кроки:
1. **Створи EC2 інстанс**:
   - Увійди в AWS Management Console.
   - Вибери "EC2" → "Launch Instance".
   - Обери AMI (наприклад, **Ubuntu 22.04**).
   - Вибери тип інстансу (наприклад, t2.micro для тестування або GPU-інстанс для інтенсивних задач).
   - Налаштуй SSH-доступ, щоб підключатися до сервера.

2. **Налаштуй сервер**:
   Підключись через SSH:
   ```bash
   ssh -i "your-key.pem" ubuntu@<INSTANCE_IP>
   ```

   Встанови необхідні залежності:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip -y
   ```

   Завантаж свій код:
   ```bash
   git clone <URL_твого_репозиторію>
   cd <назва_папки>
   pip3 install -r requirements.txt
   ```

3. **Запусти сервіс**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Налаштуй доступ до сервісу**:
   - У розділі **Security Groups** дозволь вхідний трафік на порт 8000 (або інший порт, який використовує твій сервіс).
   - Відвідай `http://<INSTANCE_IP>:8000/docs`, щоб перевірити роботу API.

---

### **2. Google Cloud Platform (GCP)**
На GCP можна використовувати Compute Engine для створення серверу або Cloud Run для безсерверного розгортання.

#### Compute Engine:
1. **Створи віртуальну машину**:
   - Увійди в GCP Console → Compute Engine → VM Instances.
   - Обери конфігурацію (OS: Ubuntu, тип машини: n1-standard-1 або потужніший).
   - Налаштуй доступ до порту (напр., 8000).

2. **Підключись до серверу**:
   Використовуй SSH-клієнт:
   ```bash
   gcloud compute ssh <назва_інстансу>
   ```

3. **Встанови Python та залежності** (аналогічно до AWS).

4. **Запусти сервер** і перевір API.

#### Cloud Run:
1. **Контейнеризація**:
   Створи Docker-образ (див. Dockerfile з попереднього пункту) та завантаж його в Google Container Registry:
   ```bash
   gcloud builds submit --tag gcr.io/<your_project_id>/easynmt-service
   ```

2. **Розгортання сервісу**:
   ```bash
   gcloud run deploy --image gcr.io/<your_project_id>/easynmt-service --platform managed
   ```

3. **Отримай URL** для доступу до API.

---

### **3. Heroku**
Heroku — простий сервіс для розгортання додатків із мінімальною кількістю налаштувань.

#### Кроки:
1. **Створи Heroku-додаток**:
   Встанови Heroku CLI:
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

   Увійди в акаунт:
   ```bash
   heroku login
   ```

   Створи додаток:
   ```bash
   heroku create <назва_додатка>
   ```

2. **Додай конфігурацію**:
   Створи `Procfile` у корені проєкту:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Деплой на Heroku**:
   Завантаж код:
   ```bash
   git add .
   git commit -m "Deploy EasyNMT API"
   git push heroku main
   ```

4. **Отримай URL**:
   Після завершення деплою Heroku надасть URL, за яким доступний сервіс.

---

### **4. Docker (універсальний варіант)**
Якщо використовуєш Docker, контейнер можна розгорнути на будь-якій платформі.

#### Кроки:
1. **Збірка Docker-образу**:
   ```bash
   docker build -t easynmt-service .
   ```

2. **Запуск локально**:
   ```bash
   docker run -p 8000:8000 easynmt-service
   ```

3. **Розгортання**:
   Завантаж образ на Docker Hub або в реєстр хмарної платформи (AWS ECR, GCP Container Registry тощо) і розгорни його на обраній платформі (наприклад, ECS на AWS чи Kubernetes).

---

### Підсумок
Якщо розгортаєш сервіс уперше, Heroku або GCP Cloud Run підходять через свою простоту. Для масштабованих або GPU-залежних задач краще обрати AWS EC2 або Kubernetes.