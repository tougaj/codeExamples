#!/usr/bin/env python

# !pip install transformers accelerate

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
import sys
import time

# Замініть 'hf_xxx...' на ваш реальний токен з https://huggingface.co/settings/tokens
token_var_name = "HF_TOKEN"
hf_token = os.getenv(token_var_name)
if hf_token is None:
    print(f"Помилка: змінна оточення '{token_var_name}' не визначена.", file=sys.stderr)
    sys.exit(1)

print(f"Використовується токен: {hf_token}")

model_name = "google/gemma-3-4b-it"
tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    token=hf_token,
    device_map="auto",
    dtype=torch.bfloat16,
)

# input_text = """Pour assurer le financement du fonds pour les infrastructures routières, le gouvernement souhaite introduire une taxe spéciale sur les e-voitures. Deux variantes sont mises en consultations
# C’est une nouvelle qui va intéresser l’ensemble des propriétaires de voitures électriques et tous ceux qui envisagent d’en faire l’acquisition. Le Conseil fédéral souhaite taxer spécifiquement ce type de véhicules d’ici 2030. La nouvelle était dans l’air depuis quelques semaines. Albert Rösti, chef du Département des transports (DETEC), l’a confirmé ce vendredi après-midi en conférence de presse à Berne. L’objectif est d’assainir le Fonds pour les routes nationales et le trafic d’agglomération (FORTA), dont les réserves ont diminué pour la première fois en 2024.
# Pour rappel, le FORTA est essentiellement financé par les taxes sur l’essence, donc par les voitures thermiques. Avec la croissance du nombre de véhicules électriques, les recettes provenant des taxes sur les huiles minérales diminuent, mettant à mal la pérennité du fonds. Avec cet impôt, le Conseil fédéral entend également introduire une certaine équité entre les automobilistes, estimant que l’infrastructure routière doit être financée par l’ensemble de ceux qui l’utilisent. Le gouvernement a ainsi lancé ce vendredi une procédure de consultation sur la question.Voir plus"""

# input_text = """Росія постійно намагається заглушати військові супутники Великої Британії. Про це заявив глава Космічного командування країни Пол Тедман в інтерв'ю BBC, цитує Bloomberg. 
# За його словами, російські війська "щотижня" активно намагаються перешкоджати військовій діяльності Великої Британії та ретельно стежать за космічними ресурсами країни. 
# "Ми бачимо, що наші супутники досить постійно заглушаються росіянами", - зауважив Тедман.
# Генерал-майор наголосив, що Велика Британія використовує близько шість спеціальних військових супутників для зв'язку та спостереження, які оснащені технологією протидії перешкодам. 
# "Вони мають на борту корисні навантаження, які можуть бачити наші супутники, і намагаються збирати з них інформацію", - підкреслив він.
# Водночас загроза космічних перешкод з боку РФ не обмежується лише Великою Британією. 
# Зокрема у вересні міністр оборони Німеччини Борис Пісторіус повідомляв, що Росія відстежувала два супутники Intelsat, які використовуються німецькими військовими.
# "Вони можуть заглушати, засліплювати, маніпулювати або кінетично порушувати роботу супутників", - зауважив він на космічній конференції в Берліні. 
# У відповідь на це минулого місяця Британія та США провели свою першу скоординовану операцію з маневруванням супутників у космосі, яку представники оборонних відомств назвали важливим кроком уперед у співпраці союзників.
# З 4 по 12 вересня американський супутник було переміщено на орбіті для перевірки британського супутника та підтвердження його належного функціонування. 
# "Завдяки професійній роботі Космічного командування США я надзвичайно задоволений і пишаюся швидким прогресом, якого ми досягаємо разом із нашими союзниками. Зараз ми разом із нашими союзниками проводимо передові орбітальні операції для захисту та оборони наших спільних національних і військових інтересів у космосі", - запевнив Тедман.
# Загроза для Європи з боку РФ - останні новини
# Раніше речниця Міністерства закордонних справ РФ Марія Захарова зробила цинічну заяву про провокації в Європі. За її словами, "ми вже перебуваємо в стані іншої форми конфлікту".
# "Усі їхні (країн Заходу - УНІАН) заяви вказують, по-перше, на те, що вони готують ланцюг провокацій. По-друге, на те, що їм потрібно виправдати свої військові бюджети", - сказала Захарова. 
# Своєю чергою президент Франції Еммануель Макрон закликав НАТО збивати російські дрони. Він вважає, що дрони, які порушують повітряний простір європейських країн, "йдуть на великий ризик".
# "Вони (дрони - УНІАН) можуть бути знищені, і крапка. Ми тут не для того, щоб давати повне попередження. Ми зробимо те, що повинні зробити, щоб зберегти цілісність нашого повітряного простору і територіальну цілісність", - підкреслив Макрон."""

input_text="""A milliárdosok szolidaritási vagyonadójáról nyújtott be törvényjavaslatot a parlamentnek Tordai Bence, független országgyűlési képviselő. A dokumentum szerint az „adó mértéke az adóalap egymilliárd forint feletti részének 1 százaléka 10 milliárd forintig, az ezt meghaladó rész 2 százaléka 100 milliárd forintig, majd az ezt meghaladó rész 3 százaléka 1000 milliárd forintig, végül az 1000 milliárd forintot meghaladó rész 98 százaléka”. Az utolsó lépcső meglehetősen durva, mivel az ezermilliárd fölötti összeg 98 százalékát kellene befizetni adónak – idézi a hvg.hu.

Ilyen ember az országban jelenleg csak egy van a Forbes listája szerint, Mészáros Lőrinc, akinek a vagyonát a lap 1749,1 milliárd forintra becsülte. Ez alapján 763 milliárd forintot kellene befizetnie, már ha elfogadná az Országgyűlés a javaslatot.

Tordai törvényjavaslata szerint a vagyonadót azoknak a magyar állampolgároknak kellene fizetni, akinek a saját tulajdonú, életvitelszerű tartózkodásra szolgáló ingatlanán túli nettó vagyona meghaladja az egymilliárd forintot. A dokumentumban felsorolta, mi minden tartozna bele a vagyonalapba: ilyen a hazai és külföldi ingatlan, ingóság, műkincs, értékpapír, vagyoni értékű jog, bankbetét, készpénz, valamint a Magyarországon vagy külföldön bejegyzett gazdasági társaság, vállalkozás, kapcsolt vállalkozások tulajdonrésze.

Az ellenzéki politikus úgy véli, a vagyonadót a megélhetési válság következményeinek enyhítésére kellene fordítani, így a közszféra utóbbi években jelentős reálbércsökkenést elszenvedett dolgozóinak – például az egészségügyi, szociális, kulturális, önkormányzati szférában dolgozók – béremelésére, szociális juttatásokra, célzott nyugdíjemelésre, valamint a méltányos ökológiai átállás finanszírozására.

A vagyonadó kérdését az elmúlt hónapokban a Tisza Párt dobta be választási ígéretként. Az ellenzéki párt 1 százalékos adót vetne ki minden 5 milliárd forintot meghaladó vagyonra. A vagyonadó minden vagyontárgyra kiterjedne majd, beleértve a nagyértékű ingóságokat (jacht, magánrepülő, festmény, sportkocsi), ingatlanokat, a céges vagyont és a külföldön található vagyontárgyakat is."""

# Повідомлення в форматі діалогу
messages = [
    {"role": "user", "content": (
        """Ти – система для сумаризації новин. Отримуєш текст статті з сайту новин будь-якою мовою.
Твоє завдання – створити коротке резюме українською мовою, яке:
- передає головні тези та основні факти статті
- зазначає ключових учасників події (якщо вони є)
- відображає час, місце та причину подій (за наявності)
- уникає другорядних деталей і цитат, що не змінюють сенс
- зберігає нейтральний та інформативний стиль без оцінок
- формулює відповідь у 3–5 реченнях."""
        "Текст для сумаризації:\n\n"
        f"{input_text}"
    )}
]
# messages = [
#     {"role": "user", "content": (
#         """Ти — професійний перекладач українською мовою.
# Отримуєш текст іншою мовою, і твоє завдання — перекласти його українською з урахуванням таких правил:
# - Використовуй природний, зрозумілий і граматично правильний український текст
# - Де доречно, застосовуй форматування Markdown (заголовки, списки, виділення тощо)
# - Замінюй лапки на українські («...»), зберігаючи їх правильне використання
# - Уникай кальки з іншої мови — добирай відповідники, які відповідають українському стилю
#  -У відповіді надай лише перекладений текст без додаткових коментарів."""
#         "Текст для перекладу:\n\n"
#         f"{input_text}"
#     )}
# ]

# Застосовуємо шаблон чату (Gemma підтримує це!)
prompt_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
print("📝 Input to model:\n", prompt_text)  # для діагностики

start_time = time.time()

inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)

word_count = len(input_text.split())
# Українська трохи довша за французьку → множимо на 1.3
estimated_tokens = int(word_count * 3) + 20  # + буфер
max_new_tokens = max(100, estimated_tokens)  # обмеження

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        # max_new_tokens=max_new_tokens, # translation
        max_new_tokens=300, # summarize
        # early_stopping=True,          # ← додаємо
        temperature=0.1,
        do_sample=True,
        repetition_penalty=1.15,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id
    )

# Декодуємо лише згенеровану частину (після input)
generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
translation = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
if '.' in translation:
    translation = translation[:translation.rfind('.')+1].strip()
end_time = time.time()


print("\n📤 Відповідь моделі:")
print(translation)
print(f"⏱️ Відповідь зайняла {end_time - start_time:.4f} секунд")
