#!/usr/bin/env python

from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
import time
from typing import Optional

model = "google/gemma-3-4b-it"
llm = LLM(model=model)
# tokenizer = llm.get_tokenizer()
tokenizer = AutoTokenizer.from_pretrained(model)


def process(prompt: str, text: str, max_new_tokens: Optional[int] = None, temperature: Optional[float] = 0.1):
    messages_list = [
        {
            "role": "user",
            "content": (f"{prompt}\n\n{text}"),
        }
    ]
    texts = tokenizer.apply_chat_template(
        messages_list,
        tokenize=False,
        add_generation_prompt=True,
    )

    # Generate outputs
    start_time = time.time()

    if max_new_tokens is None:
        word_count = len(text.split())
        # Українська трохи довша за французьку → множимо на 1.3
        estimated_tokens = int(word_count * 3) + 20  # + буфер
        max_new_tokens = max(100, estimated_tokens)  # обмеження
    # print(f"Max tokens: {max_new_tokens}")

    sampling_params = SamplingParams(
        temperature=temperature, top_p=0.95, max_tokens=max_new_tokens
    )

    outputs = llm.generate(texts, sampling_params)
    end_time = time.time()

    # Print the outputs.
    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        # print(f"📝 Prompt:\n{prompt!r},\n\n📤 Generated text:\n{generated_text!r}")
        # print(f"📤 Generated text:\n{generated_text!r}")
        print(f"📤 Generated text:\n{generated_text}")
        print(f"⏱️ Відповідь зайняла {end_time - start_time:.4f} секунд")


def summarize(text: str, max_new_tokens: Optional[int]):
    process(
        """Ти — система створення стислих новинних резюме.
Отримуєш текст статті з новинного джерела будь-якою мовою.
Твоє завдання — підготувати коротке резюме українською мовою (3–5 речень), дотримуючись таких правил:

1. **Передай головний зміст точно й стисло** — зосередься на ключових фактах, подіях і тезах.
2. Якщо в тексті є ці дані, **зазнач основних учасників, місце, час і причину події.**
3. **Уникай** другорядних деталей, прикладів, цитат, оцінних суджень і емоційного тону.
4. Дотримуйся **нейтрального, об’єктивного та інформативного стилю.**
5. Використовуй **природну, зрозумілу й граматично правильну** українську мову.
6. **У відповіді подай лише резюме** — без коментарів, пояснень, заголовків або форматування.
Текст для сумаризації:""",
        text,
        max_new_tokens=max_new_tokens,
        temperature=0.5
    )


def translate(text: str):
    process(
        """Ти — професійний перекладач української мови.
Твоє завдання — перекласти отриманий текст українською **точно за змістом**, але **природно й виразно за формою**, дотримуючись таких правил:
1. Використовуй **граматично правильну, природну та стилістично доречну** українську мову.
2. **Не перекладай дослівно.** Уникай кальок, штучних зворотів і буквальних конструкцій — замінюй їх на природні українські відповідники або ідіоматичні вирази.
3. Використовуй українські лапки **«...»** замість іноземних варіантів („...“, "...", ‘...’ тощо), дотримуючись правил пунктуації.
4. За потреби застосовуй **форматування Markdown**:
   * заголовки (`#`, `##`),
   * списки,
   * **жирний** або *курсивний* текст,
   * цитати тощо.
5. Не додавай пояснень, коментарів, приміток чи службових фраз.
6. Якщо надано текст українською, або російською мовою, то перекладати його не потрібно. В такому разі просто виведи пустий рядок.
7. **У відповіді подавай лише перекладений текст.**
"Текст для перекладу:\n\n""",
        text,
    )


def complex_processing(text: str):
    process(
        """Ти — багатофункціональна система для обробки текстів. Твоє завдання:

1. **Визначення мови:**

   * Визнач мову оригінального тексту та віддай її у форматі **ISO 639-1** (наприклад: `uk`, `ru`, `en`, `fr`).

2. **Переклад (якщо потрібно):**

   * Якщо оригінальний текст **не українською і не російською**, переклади його українською мовою.
   * Переклад має:

     * бути природним і грамотним українським текстом ✍️
     * зберігати **структуру оригіналу** (заголовки, абзаци, списки, форматування) 🏗️
     * застосовувати Markdown там, де доречно 📑
     * замінювати лапки на українські («…») 📝
     * уникати кальки та зберігати природний стиль 🌿
   * У результаті включай поле `"translation"`.

3. **Винятки:**

   * Якщо текст **українською або російською**, перекладати його не потрібно і поле `"translation"` у результаті **не включати**.

4. **Сумаризація:**

   * У будь-якому випадку створи коротке резюме (3–5 речень) українською мовою, яке:

     * передає головні факти та тези 📰
     * зазначає учасників, час, місце та причини події (якщо є) 📍
     * зберігає нейтральний і стислий стиль ⚖️

**Формат результату (JSON):**

```json
{
  "lang_original": "xx",
  "translation": "Тут перекладений текст українською зі збереженням структури…",
  "summary": "Тут стислий виклад українською…"
}
```

> Якщо мова оригіналу — `uk` або `ru`, то поле `"translation"` не включати.

**Вхід:**

```
{Текст статті}
```

**Вихід:**
JSON з:

* `lang_original` (обов’язково)
* `summary` (обов’язково)
* `translation` (лише якщо мова ≠ `uk` і ≠ `ru`).
""",
        text,
    )


texts = [
    """More than 100 million people, including at least 15 million children, use e-cigarettes, fuelling a new wave of nicotine addiction, the World Health Organization (WHO) is warning.
Children are, on average, nine times more likely than adults to vape, it says, based on available global figures.
The WHO's Dr Etienne Krug said e-cigarettes were fuelling a "new wave" of nicotine addiction. "They are marketed as harm reduction but, in reality, are hooking kids on nicotine earlier and risk undermining decades of progress."
WHO Director General, Dr Tedros, accused the tobacco industry of "agressively targeting" young people.
"Millions of people are stopping, or not taking up, tobacco use thanks to tobacco control efforts by countries around the world," he said.
"In response to this strong progress, the tobacco industry is fighting back with new nicotine products, aggressively targeting young people. Governments must act faster and stronger in implementing proven tobacco-control policies," he added.
The vaping figures are an estimate since some countries - 109 in all, and many in African and South-East Asia - do not gather data.
According to the report, as of February this year, at least 86 million e-cigarette users were adults, mostly in high-income countries.
And at least 15 million teenagers aged between 13 and 15 already vape, based on surveys from 123 countries.
While many nations have made efforts to introduce e-cigarettes regulations to tackle child vaping in recent years, by the end of 2024, 62 countries still had no policy in place, and 74 countries had no minimum age at which e-cigarettes may be purchased, says the WHO.
Meanwhile, tobacco use has been decreasing - from an estimated 1.38 billion users in 2000 to 1.2 billion in 2024.
Prevalence of tobacco use among women dropped the most - from 11% in 2010 to 6.6% in 2024.
Among men, the decrease was from 41.4% in 2010 to 32.5% in 2024.
But one in five adults globally still uses tobacco.
Smoking is linked to many diseases, including cancer.
Experts say vaping is far less harmful than cigarettes, and can help you quit smoking. It is not recommended for non-smokers.
E-cigarettes do not burn tobacco and do not produce tar or carbon monoxide, two of the most damaging elements in tobacco smoke. They contain nicotine, which can be addictive.""",
    """Le géant des télécommunications Telefonica, engagé dans un important virage stratégique destiné à accroître sa rentabilité, envisagerait de supprimer 6000 postes, selon la presse espagnole. Une information vivement démentie par le groupe. Selon le quotidien Expansion, Telefonica souhaiterait supprimer «au moins 6000» postes dans le cadre d'un plan de restructuration, une décision qui pourrait toucher «plusieurs filiales» du groupe de télécommunications.
Une porte-parole de Telefonica a pour sa part assuré que le groupe «travaillait actuellement à de nombreuses analyses dans tous les départements de l'entreprise, mais qu'aucun plan social n'était envisagé pour le moment». L'opérateur historique espagnol est engagé depuis le début d'année dans un important virage stratégique visant à se recentrer sur ses quatre principaux marchés (Espagne, Allemagne, Royaume-Uni et Brésil).
À lire aussi
Orange, Telefonica, Deutsche Telekom… Les télécoms européens succombent aux sirènes de Nvidia
Il a ainsi engagé ces derniers mois la vente de ses filiales en Colombie, en Uruguay et en Équateur, après avoir conclu la cession de ses activités en Argentine et au Pérou. Mais la moins-value constatée lors de la cession de ces filiales a pesé lourd sur les comptes de Telefonica au premier semestre, avec une perte nette atteignant le chiffre astronomique de 1,35 milliard d'euros.
Telefonica, qui emploie 100.000 personnes dans le monde, avait toutefois confirmé fin juillet ses objectifs qui prévoient une croissance organique pour 2025. Le recentrage engagé depuis le début d'année par l'opérateur espagnol survient à un moment charnière pour le géant des télécoms, au cœur de vastes manœuvres depuis l'entrée surprise de la compagnie saoudienne STC, qui a acquis 9,9% du capital de l'entreprise en septembre 2023. Cette opération avait conduit l'État espagnol à prendre une participation de 10% dans l'entreprise via le fonds public SEPI.
""",
    """Україна ще до вступу Дональда Трампа на посаду передавала американській стороні список із близько 200 російських об’єктів, які треба знищити з метою послаблення російських спроможностей на лінії фронту.
Таку думку висловив військовий аналітик, ветеран російсько-української війни, майор запасу ЗСУ Олексій Гетьман в етері на Радіо NV.
"Щодо заяв Трампа про те, що він хоче знати, куди саме ми збираємося спрямовувати ці ракети – вочевидь, не по цивільним об’єктам, як це роблять росіяни", - сказав Гетьман.
Водночас, ще майже рік тому, коли в США президентом був Джо Байден, до Америки приїздила українська делегація і передавала список із 200 об’єктів, які необхідно знищити для того, аби послабити можливості росіян щонайменше на лінії фронту.
Гетьман вважає заяву Трампа про те, що майже увалив рішення щодо можливості продажу для України ракет Tomahawk "більш популістичною".
"Він чудово знає куди і що ми збираємося знищувати, які об’єкти є критичними для нас з точки зору російської підтримки керування чи постачання всього того, що відбувається на лінії фронту", - додав Гетьман.
Він додав, що буде "непогано", якщо ракети "Томагавк" потраплять до України. "Якщо буде, то добре", - зазначив Гетьман.
Експерт переконаний, що Україна має завдавати ударів по військовим об’єктам на території РФ, і також він впевнений, що Україна буде і далі атакувати енергетичні об’єкти, які живлять військові частини і військові підприємства.
Як повідомляв УНІАН, президент США Дональд Трамп заявив, що вже наче ухвалив рішення про продаж ракет Tomahawk, але спершу хоче з’ясувати, як українці будуть застосовувати ці ракети.""",
]

for text in texts:
    translate(text)
    summarize(text, 300)
    # complex_processing(text)
