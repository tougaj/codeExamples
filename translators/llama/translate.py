#!/usr/bin/env python

# CMAKE_ARGS="-DGGML_CUDA=on \
# -DGGML_CUDA_F16=on \
# -DGGML_CUDA_GRAPH=on \
# -DCMAKE_CUDA_ARCHITECTURES=100" \
# pip install --upgrade --force-reinstall --no-cache-dir llama-cpp-python

from llama_cpp import Llama
import warnings

warnings.filterwarnings("ignore")

# ⚡ Завантаження моделі на GPU
llm = Llama(
    model_path="/data/models/lmstudio-community/gemma-3-4b-it-GGUF/gemma-3-4b-it-Q4_K_M.gguf",  # шлях до твоєї моделі
    n_ctx=2048,
    n_gpu_layers=-1,   # ✅ всі шари на GPU (якщо відеопам’яті достатньо)
    n_threads=8,       # кількість CPU-потоків (для допоміжних операцій)
    verbose=True
)

# 📌 Зашитий запит
query = """"Переклади текст нижче українською мовою. Де доречно використовуй форматування markdown. Зваж на те, що в українській мові використовуються специфічні лапки, тому заміняй їх у тексті. Виведи лише переклад. Ось текст:
Pour assurer le financement du fonds pour les infrastructures routières, le gouvernement souhaite introduire une taxe spéciale sur les e-voitures. Deux variantes sont mises en consultations
C’est une nouvelle qui va intéresser l’ensemble des propriétaires de voitures électriques et tous ceux qui envisagent d’en faire l’acquisition. Le Conseil fédéral souhaite taxer spécifiquement ce type de véhicules d’ici 2030. La nouvelle était dans l’air depuis quelques semaines. Albert Rösti, chef du Département des transports (DETEC), l’a confirmé ce vendredi après-midi en conférence de presse à Berne. L’objectif est d’assainir le Fonds pour les routes nationales et le trafic d’agglomération (FORTA), dont les réserves ont diminué pour la première fois en 2024.
Pour rappel, le FORTA est essentiellement financé par les taxes sur l’essence, donc par les voitures thermiques. Avec la croissance du nombre de véhicules électriques, les recettes provenant des taxes sur les huiles minérales diminuent, mettant à mal la pérennité du fonds. Avec cet impôt, le Conseil fédéral entend également introduire une certaine équité entre les automobilistes, estimant que l’infrastructure routière doit être financée par l’ensemble de ceux qui l’utilisent. Le gouvernement a ainsi lancé ce vendredi une procédure de consultation sur la question.Voir plus
"""

# 🚀 Запуск генерації
output = llm(
    f"<start_of_turn>user\n{query}<end_of_turn>\n<start_of_turn>model",
    max_tokens=300,
    temperature=0.7,
    stop=["<end_of_turn>"]
)

# 📝 Отримання відповіді
answer = output["choices"][0]["text"].strip()
print("Відповідь моделі:\n", answer)