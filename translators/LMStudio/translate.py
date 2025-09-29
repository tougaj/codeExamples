#!/usr/bin/env python

import lmstudio as lms

SERVER_API_HOST = "localhost:1234"
lms.configure_default_client(SERVER_API_HOST)

# model = lms.llm("google/gemma-3-4b")
# result = model.respond("""Переклади текст нижче українською мовою. виведи лише переклад. Ось текст:
# Ein Regionaljet mit 53 Passagieren und Crewmitgliedern schoss auf dem Roanoke-Blacksburg Regional Airport im amerikanischen Bundesstaat Virginia über die Landebahn hinaus und kam nicht rechtzeitig zum Stehen. Zement-Zone stoppt Flieger
# Das Flugzeug wurde jedoch erfolgreich durch ein spezielles Sicherheitssystem gestoppt: eine mit Zementblöcken ausgelegte Sicherheitszone. Dadurch wurde ein Unfall verhindert, und es gab keine Verletzten unter den Insassen, berichtet das „Wall Street Journal“.""")

# print(result)

# model_key = "google/gemma-3-4b"
model_key = "google/gemma-3-27b"
draft_model_key = "google/gemma-3-4b"


with lms.Client() as client:
    model = client.llm.model(model_key)
    result = model.respond("""Переклади текст нижче українською мовою. Де доречно використовуй форматування markdown. Зваж на те, що в українській мові використовуються специфічні лапки, тому заміняй їх у тексті. Виведи лише переклад. Ось текст:
Pour assurer le financement du fonds pour les infrastructures routières, le gouvernement souhaite introduire une taxe spéciale sur les e-voitures. Deux variantes sont mises en consultations
C’est une nouvelle qui va intéresser l’ensemble des propriétaires de voitures électriques et tous ceux qui envisagent d’en faire l’acquisition. Le Conseil fédéral souhaite taxer spécifiquement ce type de véhicules d’ici 2030. La nouvelle était dans l’air depuis quelques semaines. Albert Rösti, chef du Département des transports (DETEC), l’a confirmé ce vendredi après-midi en conférence de presse à Berne. L’objectif est d’assainir le Fonds pour les routes nationales et le trafic d’agglomération (FORTA), dont les réserves ont diminué pour la première fois en 2024.
Pour rappel, le FORTA est essentiellement financé par les taxes sur l’essence, donc par les voitures thermiques. Avec la croissance du nombre de véhicules électriques, les recettes provenant des taxes sur les huiles minérales diminuent, mettant à mal la pérennité du fonds. Avec cet impôt, le Conseil fédéral entend également introduire une certaine équité entre les automobilistes, estimant que l’infrastructure routière doit être financée par l’ensemble de ceux qui l’utilisent. Le gouvernement a ainsi lancé ce vendredi une procédure de consultation sur la question.Voir plus
""",
    config={
        "draftModel": draft_model_key,
        "temperature": 0.1,
    })

    print(result)

    stats = result.stats
    print(f"Accepted {stats.accepted_draft_tokens_count}/{stats.predicted_tokens_count} tokens")

# with lms.Client() as client:
#     model = client.llm.model("google/gemma-3-4b")
#     # model = client.llm.model("qwen/qwen3-4b")

#     for fragment in model.respond_stream("""Переклади текст нижче українською мовою. виведи лише переклад. Ось текст:
# Ein Regionaljet mit 53 Passagieren und Crewmitgliedern schoss auf dem Roanoke-Blacksburg Regional Airport im amerikanischen Bundesstaat Virginia über die Landebahn hinaus und kam nicht rechtzeitig zum Stehen. Zement-Zone stoppt Flieger
# Das Flugzeug wurde jedoch erfolgreich durch ein spezielles Sicherheitssystem gestoppt: eine mit Zementblöcken ausgelegte Sicherheitszone. Dadurch wurde ein Unfall verhindert, und es gab keine Verletzten unter den Insassen, berichtet das „Wall Street Journal“."""):
#         print(fragment.content, end="", flush=True)
#     print() # Advance to a new line at the end of the response