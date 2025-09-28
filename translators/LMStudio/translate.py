#!/usr/bin/env python

import lmstudio as lms

SERVER_API_HOST = "localhost:1234"
lms.configure_default_client(SERVER_API_HOST)

# model = lms.llm("google/gemma-3-4b")
# result = model.respond("""Переклади текст нижче українською мовою. виведи лише переклад. Ось текст:
# Ein Regionaljet mit 53 Passagieren und Crewmitgliedern schoss auf dem Roanoke-Blacksburg Regional Airport im amerikanischen Bundesstaat Virginia über die Landebahn hinaus und kam nicht rechtzeitig zum Stehen. Zement-Zone stoppt Flieger
# Das Flugzeug wurde jedoch erfolgreich durch ein spezielles Sicherheitssystem gestoppt: eine mit Zementblöcken ausgelegte Sicherheitszone. Dadurch wurde ein Unfall verhindert, und es gab keine Verletzten unter den Insassen, berichtet das „Wall Street Journal“.""")

# print(result)


with lms.Client() as client:
    model = client.llm.model("google/gemma-3-4b")
    result = model.respond("""Переклади текст нижче українською мовою. виведи лише переклад. Ось текст:
Ein Regionaljet mit 53 Passagieren und Crewmitgliedern schoss auf dem Roanoke-Blacksburg Regional Airport im amerikanischen Bundesstaat Virginia über die Landebahn hinaus und kam nicht rechtzeitig zum Stehen. Zement-Zone stoppt Flieger
Das Flugzeug wurde jedoch erfolgreich durch ein spezielles Sicherheitssystem gestoppt: eine mit Zementblöcken ausgelegte Sicherheitszone. Dadurch wurde ein Unfall verhindert, und es gab keine Verletzten unter den Insassen, berichtet das „Wall Street Journal“.""",
	config={
    	"temperature": 0.1,
	})

    print(result)

# with lms.Client() as client:
#     model = client.llm.model("google/gemma-3-4b")
#     # model = client.llm.model("qwen/qwen3-4b")

#     for fragment in model.respond_stream("""Переклади текст нижче українською мовою. виведи лише переклад. Ось текст:
# Ein Regionaljet mit 53 Passagieren und Crewmitgliedern schoss auf dem Roanoke-Blacksburg Regional Airport im amerikanischen Bundesstaat Virginia über die Landebahn hinaus und kam nicht rechtzeitig zum Stehen. Zement-Zone stoppt Flieger
# Das Flugzeug wurde jedoch erfolgreich durch ein spezielles Sicherheitssystem gestoppt: eine mit Zementblöcken ausgelegte Sicherheitszone. Dadurch wurde ein Unfall verhindert, und es gab keine Verletzten unter den Insassen, berichtet das „Wall Street Journal“."""):
#         print(fragment.content, end="", flush=True)
#     print() # Advance to a new line at the end of the response