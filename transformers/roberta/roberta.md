Зрозуміло, задача полягає в тому, щоб визначити, чи належить текст до однієї конкретної тематики (рубрики). Це дещо спрощує завдання, і можна підходити до нього як до задачі бінарної класифікації (тобто класифікації "так" або "ні").

### Як це реалізувати:

1. **Збір даних**:

   * **Позитивні приклади**: Зберіть тексти, які однозначно належать до обраної тематики.
   * **Негативні приклади**: Зберіть тексти, які не належать до цієї тематики (вони необхідні для тренування моделі розрізняти, коли текст не відповідає вашій рубриці).

2. **Підготовка даних**:

   * **Балансування вибірки**: Переконайтеся, що у вас є достатня кількість позитивних і негативних прикладів.
   * **Обробка тексту**: Використовуйте ті ж методи попередньої обробки, які згадувалися раніше (лематизація, токенізація, видалення стоп-слів тощо).

3. **Вибір моделі**:

   * Для бінарної класифікації добре підходять ті ж багатомовні моделі (наприклад, **mBERT**, **XLM-RoBERTa**), які можна fine-tune для визначення, чи належить текст до певної тематики.

4. **Fine-tuning**:

   * Використовуйте позитивні та негативні приклади для навчання моделі. Мета – навчити модель розпізнавати тексти, які відповідають вашій рубриці.
   * У моделі буде лише два класи: "належить до рубрики" (1) і "не належить" (0).

### Приклад fine-tuning для бінарної класифікації:

```python
from transformers import BertForSequenceClassification, Trainer, TrainingArguments, BertTokenizer
import torch

# Завантаження багатомовної моделі BERT
model = BertForSequenceClassification.from_pretrained('xlm-roberta-base', num_labels=2)
tokenizer = BertTokenizer.from_pretrained('xlm-roberta-base')

# Підготовка даних
inputs = tokenizer(тексти, padding=True, truncation=True, return_tensors="pt")
labels = torch.tensor([1 if label == 'позитивний' else 0 for label in labels])

# Fine-tuning моделі на даних
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    evaluation_strategy="epoch",
    save_total_limit=1,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

trainer.train()
```

5. **Оцінка моделі**:

   * Перевірте модель на тестовій вибірці, щоб переконатися, що вона коректно визначає приналежність тексту до рубрики.
   * Використовуйте метрики, такі як точність, F1-міра, для оцінки якості роботи моделі.

6. **Інференс**:

   * Подайте новий текст до моделі, і вона поверне результат, який вкаже, чи відповідає текст вашій рубриці.

```python
# Класифікація нового тексту
inputs = tokenizer("Текст для класифікації", return_tensors="pt")
outputs = model(**inputs)
logits = outputs.logits
predicted_class_id = torch.argmax(logits).item()

if predicted_class_id == 1:
    print("Текст відповідає рубриці")
else:
    print("Текст не відповідає рубриці")
```

Цей підхід дозволить вам створити систему, яка визначатиме, чи належить текст до певної тематики на основі заздалегідь визначених критеріїв.



При попередній обробці тексту (токенізація, лематизація та інше) рішення про збереження пунктуації залежить від конкретної задачі та моделі, яку ви використовуєте. Ось кілька факторів, які варто врахувати:

### 1. **Для сучасних трансформерних моделей (BERT, RoBERTa, mBERT тощо)**:

* **Пунктуація зазвичай зберігається**. Ці моделі тренувалися на текстах із пунктуацією, тому її збереження допомагає моделі краще розуміти структуру речень. Наприклад, розділові знаки можуть допомагати визначати контексти та синтаксичні структури, що покращує точність класифікації.
* Тому в більшості випадків **не потрібно видаляти знаки пунктуації**, оскільки вони можуть містити важливу інформацію для моделей трансформерів.

### 2. **Якщо ви використовуєте класичні підходи (TF-IDF, BOW)**:

* У класичних підходах пунктуація може не бути корисною і її часто **видаляють**, щоб зменшити розмірність і шум у даних.
* Однак, навіть у таких випадках, є аргументи за збереження деяких пунктуаційних знаків, таких як крапка чи знак питання, оскільки вони можуть вказувати на кінець речення або тип питання.

### 3. **Залежить від завдання**:

* Якщо ваші тексти містять специфічні шаблони або значущі розділові знаки, пунктуація може мати важливе значення (наприклад, виявлення питальних або негативних тонів у тексті).
* У задачах класифікації текстів трансформерні моделі зазвичай добре працюють з текстами, які містять пунктуацію.

### Висновок:

* Для **моделей трансформерів** (таких як BERT, RoBERTa) зберігайте пунктуацію, адже це допоможе моделі краще розуміти контекст.
* Для **класичних моделей** (TF-IDF, Bag of Words) пунктуацію можна видалити, якщо вона не несе цінної інформації.

Отже, у вашому випадку, якщо ви використовуєте багатомовні моделі трансформерів для класифікації текстів, краще **залишати пунктуацію** в тексті.



Цифри та слова з цифрами (наприклад, "COVID-19", "2024") можуть нести важливу інформацію залежно від контексту. Ось рекомендації щодо того, чи варто зберігати або видаляти цифри при попередній обробці тексту:

### 1. **Для трансформерних моделей (BERT, RoBERTa та ін.)**:

* **Цифри краще зберігати**. Моделі трансформерів добре справляються з обробкою цифр та слів із цифрами, і ці дані можуть бути важливими для класифікації.
* **Слова з цифрами**: Такі слова, як "COVID-19" або "F-35", мають значення в конкретному контексті. Видалення цифр може порушити зміст.
* **Цифри, що позначають дати, суми**: Дати, роки (наприклад, "2023") або кількості можуть бути критичними для задач, пов'язаних з аналізом текстів або хронологією подій.

### 2. **Класичні підходи (TF-IDF, Bag of Words)**:

* У класичних моделях, **цифри часто видаляються**, оскільки вони можуть бути шумом або збільшувати розмірність векторів, не додаючи значної інформації.
* Однак, якщо цифри мають специфічне значення у вашій задачі (наприклад, дати або суми), то їх можна залишити.
* **Слова з цифрами** краще залишати, оскільки вони можуть бути важливими термінами у тексті (наприклад, "COVID-19").

### 3. **Залежить від задачі**:

* Якщо цифри або слова з цифрами є критично важливими для розуміння тексту або тематики (наприклад, фінансові звіти, дати), їх обов’язково слід залишити.
* Якщо цифри не мають конкретного значення, їх можна видалити для зменшення шуму.

### Висновок:

* **Трансформерні моделі**: Залишайте цифри та слова з цифрами. Моделі добре працюють з ними, і це може бути корисно для класифікації.
* **Класичні моделі**: Можна видаляти цифри, але зберігати слова з цифрами, якщо вони мають значення для вашої задачі.

З огляду на те, що ви використовуєте трансформерні моделі, **цифри та слова з цифрами краще залишати в тексті**, оскільки вони можуть нести важливу інформацію для правильної класифікації.



Окей 👍 давай приклад коду на Python з HuggingFace 🤖

Припустимо, у нас є дані у файлі `dataset.csv` такого вигляду:

```csv
text,label
"Міністерство транспорту України оголосило новий тендер на будівництво доріг.",1
"Вчора відбувся концерт популярного гурту у Львові.",0
"Верховна Рада України ухвалила закон щодо реформування транспортної галузі.",1
"Сьогодні у Києві сонячна погода, температура +25.",0
```

---

### 🔹 Код для навчання `xlm-roberta-base`

```python
from datasets import load_dataset
from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification
from transformers import TrainingArguments, Trainer
import evaluate

# 1. Завантажуємо дані з CSV
dataset = load_dataset("csv", data_files="dataset.csv")

# 2. Завантажуємо токенайзер
tokenizer = XLMRobertaTokenizer.from_pretrained("xlm-roberta-base")

# 3. Токенізація текстів
def preprocess(example):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=256)

encoded_dataset = dataset.map(preprocess, batched=True)

# 4. Модель (2 класи: 0 і 1)
model = XLMRobertaForSequenceClassification.from_pretrained("xlm-roberta-base", num_labels=2)

# 5. Метрика для оцінки
accuracy = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = logits.argmax(axis=-1)
    return accuracy.compute(predictions=predictions, references=labels)

# 6. Аргументи тренування
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=50,
    load_best_model_at_end=True,
)

# 7. Тренер
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=encoded_dataset["train"],
    eval_dataset=encoded_dataset["train"].train_test_split(test_size=0.2)["test"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

# 8. Запуск навчання
trainer.train()

# 9. Тестуємо на новому тексті
test_text = "Міністерство транспорту запустило нову програму розвитку доріг."
inputs = tokenizer(test_text, return_tensors="pt", truncation=True, padding=True)
outputs = model(**inputs)
prediction = outputs.logits.argmax(dim=-1).item()
print("Прогноз:", prediction)  # 1 = підпадає під рубрику, 0 = ні
```

---

### 🔹 Що відбувається в коді

1. **Завантажуємо CSV** з колонками `text` та `label`.
2. **Токенізуємо** (xlm-roberta має SentencePiece, тому не треба лематизації/чистки стоп-слів).
3. **Будуємо модель** `xlm-roberta-base` з 2 виходами.
4. **Тренуємо** (3 епохи достатньо на старт).
5. **Перевіряємо** на новому реченні.

---

👉 Хочете, я ще покажу, як правильно **розбити датасет на train/test/validation** і підготувати пайплайн для ваших текстів (наприклад, українських та російських статей)?



Добре 🚀 давай зробимо повноцінний пайплайн з **розбиттям даних на train/validation/test**, щоб все було готово для навчання на ваших українсько-російських статтях.

---

### 🔹 Приклад CSV (`dataset.csv`)

```csv
text,label
"Міністерство транспорту України оголосило новий тендер на будівництво доріг.",1
"Вчора відбувся концерт популярного гурту у Львові.",0
"Верховна Рада України ухвалила закон щодо реформування транспортної галузі.",1
"Сегодня в Москве открыли новый парк для отдыха.",0
"Кабмін затвердив програму розвитку транспортної інфраструктури на 2024 рік.",1
```

---

### 🔹 Повний код пайплайну

```python
from datasets import load_dataset
from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification
from transformers import TrainingArguments, Trainer
import evaluate
import numpy as np

# 1. Завантажуємо датасет із CSV
dataset = load_dataset("csv", data_files="dataset.csv")

# 2. Розбиваємо на train/validation/test
# 80% train, 10% validation, 10% test
dataset = dataset["train"].train_test_split(test_size=0.2, seed=42)
test_valid = dataset["test"].train_test_split(test_size=0.5, seed=42)
dataset["validation"] = test_valid["train"]
dataset["test"] = test_valid["test"]

print(dataset)

# 3. Завантажуємо токенайзер
tokenizer = XLMRobertaTokenizer.from_pretrained("xlm-roberta-base")

# 4. Функція токенізації
def preprocess(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=256
    )

encoded_dataset = dataset.map(preprocess, batched=True)

# 5. Модель
model = XLMRobertaForSequenceClassification.from_pretrained(
    "xlm-roberta-base",
    num_labels=2  # 0 = не підпадає, 1 = підпадає
)

# 6. Метрики
accuracy = evaluate.load("accuracy")
f1 = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy.compute(predictions=predictions, references=labels)["accuracy"],
        "f1": f1.compute(predictions=predictions, references=labels, average="weighted")["f1"]
    }

# 7. Аргументи тренування
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir="./logs",
    load_best_model_at_end=True,
    metric_for_best_model="f1"
)

# 8. Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=encoded_dataset["train"],
    eval_dataset=encoded_dataset["validation"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# 9. Навчання
trainer.train()

# 10. Оцінка на тесті
results = trainer.evaluate(encoded_dataset["test"])
print("Test results:", results)

# 11. Тестуємо на новому тексті
test_text = "Верховна Рада ухвалила новий транспортний закон."
inputs = tokenizer(test_text, return_tensors="pt", truncation=True, padding=True)
outputs = model(**inputs)
prediction = outputs.logits.argmax(dim=-1).item()
print("Прогноз:", prediction)  # 1 = підпадає під рубрику
```

---

### 🔹 Що тут відбувається

1. **CSV → Dataset** через `load_dataset`.
2. Розбиваємо на `train` (80%), `validation` (10%), `test` (10%).
3. Токенізація (`max_length=256` достатньо для новин/статей).
4. Модель `xlm-roberta-base` (можна замінити на `xlm-roberta-large` для кращої точності).
5. Метрики: `accuracy` + `f1` (для балансування у випадку нерівних класів).
6. Використання **`Trainer`** спрощує навчання/оцінку.
7. Після навчання можна давати новий текст і отримувати прогноз (`0` або `1`).

---

⚡️ Так ви отримаєте готовий класифікатор, який працює з українськими та російськими текстами.

---

Хочете, я ще підкажу, **як зберегти готову модель і потім швидко використовувати її для нових текстів** (без повторного навчання)?



Чудово 💾✨
Після того, як ви натренували `xlm-roberta`, її можна **зберегти** та потім **вантажити без повторного навчання**. Це робиться дуже просто через HuggingFace.

---

### 🔹 Збереження моделі після навчання

```python
# Зберігаємо модель і токенайзер у локальну папку
model.save_pretrained("./my_rubric_model")
tokenizer.save_pretrained("./my_rubric_model")
```

У папці `./my_rubric_model` збережуться файли:

* `pytorch_model.bin` — ваги моделі
* `config.json` — конфіг
* `tokenizer.json`, `vocab.json`, `merges.txt` — токенайзер
* `special_tokens_map.json` і `tokenizer_config.json`

---

### 🔹 Завантаження моделі для використання

```python
from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification

# Завантажуємо модель і токенайзер
tokenizer = XLMRobertaTokenizer.from_pretrained("./my_rubric_model")
model = XLMRobertaForSequenceClassification.from_pretrained("./my_rubric_model")

# Класифікація нового тексту
test_text = "Кабмін затвердив програму розвитку транспортної інфраструктури."
inputs = tokenizer(test_text, return_tensors="pt", truncation=True, padding=True)
outputs = model(**inputs)

prediction = outputs.logits.argmax(dim=-1).item()
print("Прогноз:", prediction)  # 1 = підпадає під рубрику, 0 = ні
```

---

### 🔹 Варіант з `pipeline` (ще простіше)

```python
from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="./my_rubric_model",
    tokenizer="./my_rubric_model"
)

print(classifier("Верховна Рада ухвалила закон щодо реформування транспорту."))
```

👉 Вивід буде приблизно такий:

```python
[{'label': 'LABEL_1', 'score': 0.95}]
```

---

### 🔹 Додатково

* Якщо модель **добре працює**, можна залити її на HuggingFace Hub і потім викликати з будь-якої машини.
* Якщо потрібно **дуже швидке застосування у продакшені**, можна:

  * експортувати у **ONNX** для інференсу на CPU,
  * або використати **Optimum** від HuggingFace для оптимізації.

---

Хочете, я покажу, як **експортувати натреновану модель у ONNX**, щоб вона працювала швидше (наприклад, у продакшені на CPU)?



