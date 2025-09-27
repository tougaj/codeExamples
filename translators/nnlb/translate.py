#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для автоматичного перекладу з будь-якої підтримуваної мови на українську
з використанням NLLB-200-3.3B від Facebook
"""

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import warnings
from typing import Optional

# Приховуємо попередження для чистоти виводу
warnings.filterwarnings("ignore")

# Імпортуємо langdetect для визначення мови
try:
    from langdetect import detect, LangDetectError
    print("📚 Використовуємо langdetect для визначення мови")
except ImportError:
    print("❌ Помилка: Установіть langdetect за допомогою: pip install langdetect")
    exit(1)

class NLLBToUkrainianTranslator:
    def __init__(self):
        """Ініціалізація моделі та токенізатора"""
        print("🔧 Завантаження моделі NLLB-200-3.3B...")
        
        self.model_name = "facebook/nllb-200-3.3B"
        
        # Важливо: use_fast=False для коректної роботи з мовними токенами
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=False)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        self.target_lang = 'ukr_Cyrl'
        
        # Перевірка завантаження мов
        lang_tokens = [t for t in self.tokenizer.additional_special_tokens if t.startswith(">>")]
        print(f"✅ Завантажено {len(lang_tokens)} мовних токенів")
        print(f"🇺🇦 Цільова мова: Українська ({self.target_lang})")

        test_token = ">>por_Latn<<"
        token_id = self.tokenizer.convert_tokens_to_ids(test_token)
        print(f"Токен '{test_token}' → ID: {token_id}")
        print(f"UNK ID: {self.tokenizer.unk_token_id}")
        print(f"Чи підтримується? {token_id != self.tokenizer.unk_token_id}")
                
    def get_language_mapping(self):
        """
        Повний маппінг ISO кодів на NLLB коди для моделі facebook/nllb-200-3.3B
        Підтримує 200+ мов з різних мовних сімей та письмових систем
        """
        return {
            # ============ ЄВРОПЕЙСЬКІ МОВИ ============
            
            # Слов'янські мови
            'uk': 'ukr_Cyrl',      # українська
            'ru': 'rus_Cyrl',      # російська
            'be': 'bel_Cyrl',      # білоруська
            'bg': 'bul_Cyrl',      # болгарська
            'mk': 'mkd_Cyrl',      # македонська
            'sr': 'srp_Cyrl',      # сербська (кирилиця)
            'hr': 'hrv_Latn',      # хорватська
            'bs': 'bos_Latn',      # боснійська
            'me': 'cnr_Latn',      # чорногорська
            'sl': 'slv_Latn',      # словенська
            'pl': 'pol_Latn',      # польська
            'cs': 'ces_Latn',      # чеська
            'sk': 'slk_Latn',      # словацька
            
            # Германські мови
            'en': 'eng_Latn',      # англійська
            'de': 'deu_Latn',      # німецька
            'nl': 'nld_Latn',      # нідерландська
            'af': 'afr_Latn',      # африкаанс
            'sv': 'swe_Latn',      # шведська
            'da': 'dan_Latn',      # данська
            'no': 'nob_Latn',      # норвезька (букмол)
            'nn': 'nno_Latn',      # норвезька (нюношк)
            'is': 'isl_Latn',      # ісландська
            'fo': 'fao_Latn',      # фарерська
            'fy': 'fry_Latn',      # західнофризька
            'lb': 'ltz_Latn',      # люксембурзька
            'yi': 'yid_Hebr',      # їдиш
            
            # Романські мови
            'fr': 'fra_Latn',      # французька
            'es': 'spa_Latn',      # іспанська
            'pt': 'por_Latn',      # португальська
            'it': 'ita_Latn',      # італійська
            'ro': 'ron_Latn',      # румунська
            'ca': 'cat_Latn',      # каталанська
            'gl': 'glg_Latn',      # галісійська
            'eu': 'eus_Latn',      # баскська
            'oc': 'oci_Latn',      # окситанська
            'sc': 'srd_Latn',      # сардинська
            'co': 'cos_Latn',      # корсиканська
            'rm': 'roh_Latn',      # ретороманська
            'wa': 'wln_Latn',      # валлонська
            'ast': 'ast_Latn',     # астурійська
            'an': 'arg_Latn',      # арагонська
            'mwl': 'mwl_Latn',     # мірандська
            'ext': 'ext_Latn',     # екстремадурська
            
            # Кельтські мови
            'ga': 'gle_Latn',      # ірландська
            'gd': 'gla_Latn',      # шотландська гельська
            'cy': 'cym_Latn',      # валлійська
            'br': 'bre_Latn',      # бретонська
            'gv': 'glv_Latn',      # менська
            'kw': 'cor_Latn',      # корнська
            
            # Балтійські мови
            'lt': 'lit_Latn',      # литовська
            'lv': 'lav_Latn',      # латвійська
            
            # Фіно-угорські мови
            'fi': 'fin_Latn',      # фінська
            'et': 'est_Latn',      # естонська
            'hu': 'hun_Latn',      # угорська
            
            # Інші європейські
            'el': 'ell_Grek',      # грецька
            'mt': 'mlt_Latn',      # мальтійська
            'sq': 'als_Latn',      # албанська
            
            # ============ АЗІЙСЬКІ МОВИ ============
            
            # Китайська група
            'zh': 'zho_Hans',      # китайська (спрощена)
            'zh-cn': 'zho_Hans',   # китайська (спрощена)
            'zh-tw': 'zho_Hant',   # китайська (традиційна)
            'zh-hk': 'zho_Hant',   # китайська (Гонконг)
            'yue': 'yue_Hant',     # кантонська
            'wuu': 'wuu_Hans',     # у (шанхайська)
            'nan': 'min_Latn',     # мінь нань
            
            # Японська
            'ja': 'jpn_Jpan',      # японська
            
            # Корейська
            'ko': 'kor_Hang',      # корейська
            
            # В'єтнамська
            'vi': 'vie_Latn',      # в'єтнамська
            
            # Тайська група
            'th': 'tha_Thai',      # тайська
            'lo': 'lao_Laoo',      # лаоська
            
            # Бірманська група
            'my': 'mya_Mymr',      # бірманська
            
            # Кхмерська
            'km': 'khm_Khmr',      # кхмерська
            
            # Малайська група
            'ms': 'zsm_Latn',      # малайська
            'id': 'ind_Latn',      # індонезійська
            'jv': 'jav_Latn',      # яванська
            'su': 'sun_Latn',      # сунданська
            'min': 'min_Latn',     # мінангкабау
            'ace': 'ace_Latn',     # ачехська
            'ban': 'ban_Latn',     # балійська
            'bjn': 'bjn_Latn',     # банджарська
            'bug': 'bug_Latn',     # бугійська
            'mad': 'mad_Latn',     # мадурська
            
            # Філіппінські мови
            'tl': 'tgl_Latn',      # тагальська (філіппінська)
            'ceb': 'ceb_Latn',     # себуано
            'ilo': 'ilo_Latn',     # ілоканська
            'hil': 'hil_Latn',     # хілігайнон
            'war': 'war_Latn',     # варай
            'pam': 'pam_Latn',     # пампанган
            'pag': 'pag_Latn',     # пангасінанська
            'bcl': 'bcl_Latn',     # бікольська
            
            # Тибето-бірманські
            'bo': 'bod_Tibt',      # тибетська
            'dz': 'dzo_Tibt',      # дзонг-кха (бутанська)
            'ne': 'npi_Deva',      # непальська
            'new': 'new_Deva',     # неварська
            
            # ============ ІНДІЙСЬКІ МОВИ ============
            
            # Індоарійські мови
            'hi': 'hin_Deva',      # гінді
            'ur': 'urd_Arab',      # урду
            'bn': 'ben_Beng',      # бенгальська
            'pa': 'pan_Guru',      # панджабі
            'gu': 'guj_Gujr',      # гуджараті
            'mr': 'mar_Deva',      # маратхі
            'or': 'ory_Orya',      # орія
            'as': 'asm_Beng',      # ассамська
            'bho': 'bho_Deva',     # бходжпурі
            'mai': 'mai_Deva',     # майтхілі
            'mag': 'mag_Deva',     # магахі
            'sa': 'san_Deva',      # санскрит
            'sd': 'snd_Arab',      # сіндхі
            'si': 'sin_Sinh',      # сінгальська
            'dv': 'div_Thaa',      # мальдівська
            
            # Дравідійські мови
            'ta': 'tam_Taml',      # тамільська
            'te': 'tel_Telu',      # телугу
            'ml': 'mal_Mlym',      # малаялам
            'kn': 'kan_Knda',      # каннада
            
            # ============ БЛИЗЬКОСХІДНІ МОВИ ============
            
            # Семітські мови
            'ar': 'arb_Arab',      # арабська (сучасна літературна)
            'arz': 'arz_Arab',     # єгипетська арабська
            'acm': 'acm_Arab',     # месопотамська арабська
            'apc': 'apc_Arab',     # левантійська арабська
            'acq': 'acq_Arab',     # та'ізі-аденська арабська
            'ajp': 'ajp_Arab',     # південнолевантійська арабська
            'ars': 'ars_Arab',     # наджді арабська
            'ary': 'ary_Arab',     # марокканська арабська
            'he': 'heb_Hebr',      # іврит
            'mt': 'mlt_Latn',      # мальтійська
            'am': 'amh_Ethi',      # амхарська
            'ti': 'tir_Ethi',      # тигринья
            
            # Іранські мови
            'fa': 'pes_Arab',      # перська (фарсі)
            'tg': 'tgk_Cyrl',      # таджицька
            'ps': 'pbt_Arab',      # пашто
            'ku': 'ckb_Arab',      # курдська (сорані)
            'kmr': 'kmr_Latn',     # курдська (курманджі)
            'os': 'oss_Cyrl',      # осетинська
            
            # Тюркські мови
            'tr': 'tur_Latn',      # турецька
            'az': 'azj_Latn',      # азербайджанська
            'kk': 'kaz_Cyrl',      # казахська
            'ky': 'kir_Cyrl',      # киргизька
            'uz': 'uzn_Latn',      # узбецька
            'tk': 'tuk_Latn',      # туркменська
            'tt': 'tat_Cyrl',      # татарська
            'ba': 'bak_Cyrl',      # башкирська
            'chv': 'chv_Cyrl',     # чуваська
            'sah': 'sah_Cyrl',     # якутська
            'tyv': 'tyv_Cyrl',     # тувинська
            'ug': 'uig_Arab',      # уйгурська
            
            # ============ КАВКАЗЬКІ МОВИ ============
            'ka': 'kat_Geor',      # грузинська
            'hy': 'hye_Armn',      # вірменська
            'ab': 'abk_Cyrl',      # абхазька
            'ce': 'che_Cyrl',      # чеченська
            
            # ============ АФРИКАНСЬКІ МОВИ ============
            
            # Нігеро-конголезькі мови
            'sw': 'swh_Latn',      # суахілі
            'yo': 'yor_Latn',      # йоруба
            'ig': 'ibo_Latn',      # ігбо
            'ha': 'hau_Latn',      # хауса
            'zu': 'zul_Latn',      # зулу
            'xh': 'xho_Latn',      # кхоса
            'st': 'sot_Latn',      # сесото
            'tn': 'tsn_Latn',      # тсвана
            've': 'ven_Latn',      # венда
            'ts': 'tso_Latn',      # тсонга
            'ss': 'ssw_Latn',      # свазі
            'nr': 'nbl_Latn',      # південна ндебеле
            'nso': 'nso_Latn',     # північна сото
            'lg': 'lug_Latn',      # луганда
            'rw': 'kin_Latn',      # кіньяруанда
            'rn': 'run_Latn',      # кірунді
            'sn': 'sna_Latn',      # шона
            'ny': 'nya_Latn',      # чічева
            'bem': 'bem_Latn',     # бемба
            'lmo': 'lmo_Latn',     # ломбардська
            'vec': 'vec_Latn',     # венетська
            'scn': 'scn_Latn',     # сицилійська
            'nap': 'nap_Latn',     # неаполітанська
            'lij': 'lij_Latn',     # лігурійська
            'pms': 'pms_Latn',     # п'ємонтська
            
            # Нілосахарські мови
            'so': 'som_Latn',      # сомалійська
            
            # ============ АМЕРИКАНСЬКІ МОВИ ============
            'qu': 'quy_Latn',      # кечуа
            'gn': 'grn_Latn',      # гуарані
            'ay': 'aym_Latn',      # аймара
            'nah': 'nah_Latn',     # науатль
            
            # ============ ОКЕАНІЙСЬКІ МОВИ ============
            'mi': 'mri_Latn',      # маорі
            'haw': 'haw_Latn',     # гавайська
            'fj': 'fij_Latn',      # фіджійська
            'sm': 'smo_Latn',      # самоанська
            'to': 'ton_Latn',      # тонганська
            
            # ============ ШТУЧНІ МОВИ ============
            'eo': 'epo_Latn',      # есперанто
            'ia': 'ina_Latn',      # інтерлінгва
            'ie': 'ile_Latn',      # окциденталь
            'vo': 'vol_Latn',      # волапюк
            'jbo': 'jbo_Latn',     # ложбан
            
            # ============ МЕРТВІ МОВИ ============
            'la': 'lat_Latn',      # латинська
            'grc': 'grc_Grek',     # давньогрецька
            'got': 'got_Goth',     # готська
            'ang': 'ang_Latn',     # давньоанглійська
            'non': 'non_Latn',     # давньонорвезька
            'cu': 'chu_Cyrl',      # церковнослов'янська
            
            # ============ РЕГІОНАЛЬНІ ВАРІАНТИ ============
            'pt-br': 'por_Latn',   # португальська (Бразилія)
            'pt-pt': 'por_Latn',   # португальська (Португалія)
            'es-es': 'spa_Latn',   # іспанська (Іспанія)
            'es-mx': 'spa_Latn',   # іспанська (Мексика)
            'en-us': 'eng_Latn',   # англійська (США)
            'en-gb': 'eng_Latn',   # англійська (Великобританія)
            'fr-fr': 'fra_Latn',   # французька (Франція)
            'fr-ca': 'fra_Latn',   # французька (Канада)
            
            # ============ ДОДАТКОВІ ISO КОДИ ============
            'srp': 'srp_Cyrl',     # сербська (ISO 639-3)
            'hrv': 'hrv_Latn',     # хорватська (ISO 639-3)
            'bos': 'bos_Latn',     # боснійська (ISO 639-3)
            'mon': 'khk_Cyrl',     # монгольська
            'mn': 'khk_Cyrl',      # монгольська (скорочено)
            'deu': 'deu_Latn',     # німецька (ISO 639-3)
            'fra': 'fra_Latn',     # французька (ISO 639-3)
            'spa': 'spa_Latn',     # іспанська (ISO 639-3)
            'ita': 'ita_Latn',     # італійська (ISO 639-3)
            'por': 'por_Latn',     # португальська (ISO 639-3)
            'rus': 'rus_Cyrl',     # російська (ISO 639-3)
            'ukr': 'ukr_Cyrl',     # українська (ISO 639-3)
            'pol': 'pol_Latn',     # польська (ISO 639-3)
            'ces': 'ces_Latn',     # чеська (ISO 639-3)
            'slk': 'slk_Latn',     # словацька (ISO 639-3)
            'hun': 'hun_Latn',     # угорська (ISO 639-3)
            'ron': 'ron_Latn',     # румунська (ISO 639-3)
            'bul': 'bul_Cyrl',     # болгарська (ISO 639-3)
            'ell': 'ell_Grek',     # грецька (ISO 639-3)
            'tur': 'tur_Latn',     # турецька (ISO 639-3)
            'ara': 'arb_Arab',     # арабська (ISO 639-3)
            'heb': 'heb_Hebr',     # іврит (ISO 639-3)
            'fas': 'pes_Arab',     # перська (ISO 639-3)
            'hin': 'hin_Deva',     # гінді (ISO 639-3)
            'ben': 'ben_Beng',     # бенгальська (ISO 639-3)
            'tam': 'tam_Taml',     # тамільська (ISO 639-3)
            'tel': 'tel_Telu',     # телугу (ISO 639-3)
            'mar': 'mar_Deva',     # маратхі (ISO 639-3)
            'guj': 'guj_Gujr',     # гуджараті (ISO 639-3)
            'kan': 'kan_Knda',     # каннада (ISO 639-3)
            'mal': 'mal_Mlym',     # малаялам (ISO 639-3)
            'pan': 'pan_Guru',     # панджабі (ISO 639-3)
            'urd': 'urd_Arab',     # урду (ISO 639-3)
            'nep': 'npi_Deva',     # непальська (ISO 639-3)
            'sin': 'sin_Sinh',     # сінгальська (ISO 639-3)
            'tha': 'tha_Thai',     # тайська (ISO 639-3)
            'lao': 'lao_Laoo',     # лаоська (ISO 639-3)
            'mya': 'mya_Mymr',     # бірманська (ISO 639-3)
            'khm': 'khm_Khmr',     # кхмерська (ISO 639-3)
            'vie': 'vie_Latn',     # в'єтнамська (ISO 639-3)
            'ind': 'ind_Latn',     # індонезійська (ISO 639-3)
            'msa': 'zsm_Latn',     # малайська (ISO 639-3)
            'tgl': 'tgl_Latn',     # тагальська (ISO 639-3)
            'jpn': 'jpn_Jpan',     # японська (ISO 639-3)
            'kor': 'kor_Hang',     # корейська (ISO 639-3)
            'zho': 'zho_Hans',     # китайська (ISO 639-3)
            'swe': 'swe_Latn',     # шведська (ISO 639-3)
            'dan': 'dan_Latn',     # данська (ISO 639-3)
            'nor': 'nob_Latn',     # норвезька (ISO 639-3)
            'fin': 'fin_Latn',     # фінська (ISO 639-3)
            'est': 'est_Latn',     # естонська (ISO 639-3)
            'lav': 'lav_Latn',     # латвійська (ISO 639-3)
            'lit': 'lit_Latn',     # литовська (ISO 639-3)
            'slv': 'slv_Latn',     # словенська (ISO 639-3)
            'hrv': 'hrv_Latn',     # хорватська (ISO 639-3)
            'srp': 'srp_Cyrl',     # сербська (ISO 639-3)
            'bos': 'bos_Latn',     # боснійська (ISO 639-3)
            'mkd': 'mkd_Cyrl',     # македонська (ISO 639-3)
            'bel': 'bel_Cyrl',     # білоруська (ISO 639-3)
            'kat': 'kat_Geor',     # грузинська (ISO 639-3)
            'hye': 'hye_Armn',     # вірменська (ISO 639-3)
            'kaz': 'kaz_Cyrl',     # казахська (ISO 639-3)
            'kir': 'kir_Cyrl',     # киrgизька (ISO 639-3)
            'uzb': 'uzn_Latn',     # узбецька (ISO 639-3)
            'tgk': 'tgk_Cyrl',     # таджицька (ISO 639-3)
            'tuk': 'tuk_Latn',     # туркменська (ISO 639-3)
            'aze': 'azj_Latn',     # азербайджанська (ISO 639-3)
            'afr': 'afr_Latn',     # африкаанс (ISO 639-3)
            'swa': 'swh_Latn',     # суахілі (ISO 639-3)
            'yor': 'yor_Latn',     # йоруба (ISO 639-3)
            'hau': 'hau_Latn',     # хауса (ISO 639-3)
            'ibo': 'ibo_Latn',     # ігбо (ISO 639-3)
            'zul': 'zul_Latn',     # зулу (ISO 639-3)
            'xho': 'xho_Latn',     # кхоса (ISO 639-3)
            'amh': 'amh_Ethi',     # амхарська (ISO 639-3)
            'som': 'som_Latn',     # сомалійська (ISO 639-3)
        }    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Визначення мови тексту з використанням langdetect
        """
        if not text.strip():
            return 'eng_Latn'
        
        mapping = self.get_language_mapping()
        
        try:
            detected = detect(text.lower())
            print(f"🔍 langdetect визначив: {detected}")
            
            # Мапимо на NLLB код
            nllb_code = mapping.get(detected)
            if nllb_code:
                return nllb_code
            else:
                print(f"⚠️  Мова '{detected}' не знайдена в маппінгу, використовуємо англійську")
                return 'eng_Latn'
                
        except Error as e:
            print(f"⚠️  langdetect помилка: {e}, використовуємо англійську")
            return 'eng_Latn'
    
    def translate_to_ukrainian(self, text: str, source_lang: Optional[str] = None, max_length: int = 400) -> tuple:
        """
        Перекладає текст на українську мову
        """
        try:
            if not text.strip():
                return "", "unknown"

            # Визначаємо мову, якщо не задано
            if source_lang is None:
                source_lang = self.detect_language(text)
                print(f"🔍 Визначено мову: {source_lang}")
            else:
                # Якщо користувач ввів ISO-код (наприклад, 'en'), конвертуємо в NLLB
                mapping = self.get_language_mapping()
                if source_lang in mapping:
                    source_lang = mapping[source_lang]
                elif source_lang not in self.get_all_nllb_codes():
                    # Якщо це не ISO і не NLLB — спробуємо вважати, що це NLLB
                    pass  # залишаємо як є

            # Якщо вже українська — повертаємо
            if source_lang == self.target_lang:
                return text, source_lang

            # Перевірка: чи існує токен мови джерела?
            src_token = f">>{source_lang}<<"
            src_token_id = self.tokenizer.convert_tokens_to_ids(src_token)
            if src_token_id == self.tokenizer.unk_token_id:
                return f"❌ Невідома мова джерела: '{source_lang}'", source_lang

            # Перевірка: чи існує токен цільової мови?
            tgt_token = f">>{self.target_lang}<<"
            tgt_token_id = self.tokenizer.convert_tokens_to_ids(tgt_token)
            if tgt_token_id == self.tokenizer.unk_token_id:
                return f"❌ Невідома цільова мова: '{self.target_lang}'", source_lang

            # Формуємо вхідний текст з префіксом мови
            input_text = f"{src_token} {text}"
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)

            # Генерація
            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=tgt_token_id,
                    max_length=max_length,
                    num_beams=4,
                    length_penalty=1.0,
                    early_stopping=True,
                    do_sample=False  # для детермінованого результату
                )

            translation = self.tokenizer.decode(generated_tokens[0], skip_special_tokens=True)
            return translation, source_lang

        except Exception as e:
            return f"❌ Помилка перекладу: {str(e)}", source_lang or "unknown"

def main():
    """Основна функція з прикладами використання"""
    print("🇺🇦 Автоматичний переклад на українську мову")
    print("🌐 Використовується NLLB-200-3.3B")
    print("=" * 60)
    
    # Ініціалізуємо перекладач
    translator = NLLBToUkrainianTranslator()
    
    # Приклади перекладу з різних мов
    examples = [
        "Hello, how are you today? I hope everything is going well!",
        "Bonjour! Comment ça va? J'espère que vous allez bien.",
        "Hola, ¿cómo estás? Espero que tengas un buen día.",
        "Guten Tag! Wie geht es Ihnen? Ich hoffe, alles ist in Ordnung.",
        "Ciao! Come stai? Spero che tu stia bene oggi.",
        "你好！你今天怎么样？希望你一切都好！",
        "こんにちは！元気ですか？今日はいい日になりそうですね。",
        "안녕하세요! 오늘 어떻게 지내세요? 좋은 하루 되세요!",
        "Привет! Как дела? Надеюсь, у тебя всё хорошо.",
        "Cześć! Jak się masz? Mam nadzieję, że wszystko w porządku.",
        "Olá! Como você está? Espero que esteja tudo bem!",
    ]
    
    print(f"\n🔄 Приклади автоматичного перекладу:")
    print("=" * 60)
    
    for i, text in enumerate(examples, 1):
        print(f"\n📝 Приклад {i}:")
        print(f"Оригінал: {text}")
        print("🔄 Перекладаємо...")
        
        translation, detected_lang = translator.translate_to_ukrainian(text)
        
        print(f"🔍 Мова: {detected_lang}")
        print(f"🇺🇦 Переклад: {translation}")
        print("-" * 50)
    
    # Інтерактивний режим
    print(f"\n🎯 Інтерактивний режим перекладу")
    print("Введіть текст будь-якою підтримуваною мовою")
    print("(або 'exit' для виходу)")
    
    while True:
        try:
            text = input("\n📝 Введіть текст: ").strip()
            if text.lower() in ['exit', 'quit', 'вихід']:
                break
                
            if not text:
                continue
            
            # Запитуємо чи вказати мову вручну
            manual_lang = input("🔤 Вказати мову вручну? (Enter для автовизначення): ").strip()
            source_lang = manual_lang if manual_lang else None
                
            print("🔄 Перекладаємо на українську...")
            translation, detected_lang = translator.translate_to_ukrainian(text, source_lang)
            
            print(f"🔍 Мова джерела: {detected_lang}")
            print(f"🇺🇦 Український переклад: {translation}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Помилка: {e}")
    
    print("\n👋 Дякую за використання українського перекладача!")
    print("🇺🇦 Слава Україні!")

if __name__ == "__main__":
    main()