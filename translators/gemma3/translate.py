#!/usr/bin/env python

# !pip install transformers accelerate

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
import sys

# Замініть 'hf_xxx...' на ваш реальний токен з https://huggingface.co/settings/tokens
token_var_name = "HF_TOKEN"
hf_token = os.getenv(token_var_name)
if hf_token is None:
    print(f"Помилка: змінна оточення '{token_var_name}' не визначена.", file=sys.stderr)
    sys.exit(1)

print(f"Використовується токен: {hf_token}")

model = "google/gemma-3-4b-it"

tokenizer = AutoTokenizer.from_pretrained(model, token=hf_token)
model = AutoModelForCausalLM.from_pretrained(
    model,
    token=hf_token,
    device_map="auto",
    torch_dtype=torch.bfloat16,
)

input_text = """Переклади текст нижче українською мовою. виведи лише переклад. Ось текст:
Ein Regionaljet mit 53 Passagieren und Crewmitgliedern schoss auf dem Roanoke-Blacksburg Regional Airport im amerikanischen Bundesstaat Virginia über die Landebahn hinaus und kam nicht rechtzeitig zum Stehen. Zement-Zone stoppt Flieger."""

# ✅ ПРАВИЛЬНА токенізація
inputs = tokenizer(input_text, return_tensors="pt")

# ✅ ПРАВИЛЬНЕ переміщення на GPU (якщо є CUDA)
if torch.cuda.is_available():
    inputs = inputs.to("cuda")
    model = model.to("cuda")

# # ✅ ПРАВИЛЬНА генерація з параметрами
with torch.no_grad():
    outputs = model.generate(
        inputs.input_ids,                    # ✅ Правильний доступ до input_ids
        attention_mask=inputs.attention_mask, # ✅ Додаємо attention_mask
        max_new_tokens=300,                  # ✅ Достатньо токенів для перекладу
        temperature=0.1,                     # ✅ Низька температура для точності
        do_sample=True,                      # ✅ Увімкнути семплінг
        repetition_penalty=1.1,              # ✅ Уникнути повторів
        pad_token_id=tokenizer.eos_token_id, # ✅ Правильний pad_token
        eos_token_id=tokenizer.eos_token_id  # ✅ Правильний eos_token
    )

# ✅ ПРАВИЛЬНЕ декодування
full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("📤 Повна відповідь:")
print(full_response)

print("\n✅ Готово!")

# ========================================
# 💡 АЛЬТЕРНАТИВНИЙ ВАРІАНТ З КРАЩИМ ПРОМПТОМ
# ========================================

print("\n" + "="*50)
print("🔄 Пробуємо з іншим промптом...")

# Більш чіткий промпт
better_prompt = f"""<start_of_turn>user
Translate this German text to Ukrainian:

{input_text.split('Ось текст:')[-1].strip()}
<end_of_turn>
<start_of_turn>model
"""

inputs2 = tokenizer(better_prompt, return_tensors="pt")
if torch.cuda.is_available():
    inputs2 = inputs2.to("cuda")

with torch.no_grad():
    outputs2 = model.generate(
        inputs2.input_ids,
        max_new_tokens=300,
        temperature=0.1,
        do_sample=True,
        repetition_penalty=1.1,
        pad_token_id=tokenizer.eos_token_id
    )

response2 = tokenizer.decode(outputs2[0], skip_special_tokens=True)
print("📤 Відповідь з новим промптом:")
print(response2)
