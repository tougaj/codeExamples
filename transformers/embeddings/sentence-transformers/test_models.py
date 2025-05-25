#!/usr/bin/env python

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import time
import numpy as np

def compare_models():
    print("🔄 Завантажуємо моделі...")
    
    # Завантажуємо обидві моделі
    labse = SentenceTransformer('sentence-transformers/LaBSE')
    minilm = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    
    print("✅ Моделі завантажені!")
    
    # Тестові фрази - однакові поняття різними мовами
    test_pairs = [
        ("Червоний автомобіль", "Red car"),           # укр-англ
        ("Красная машина", "Red car"),                # рус-англ  
        ("Червоний автомобіль", "Красная машина"),    # укр-рус
        ("Синій будинок", "Blue house"),              # укр-англ
        ("Зелений стіл", "Green table"),             # укр-англ
        ("Чорний кіт", "Black cat"),                 # укр-англ
    ]
    
    # Додаткові тести для однієї мови
    same_language_pairs = [
        ("Червоний автомобіль", "Автомобіль червоного кольору"),  # парафраз укр
        ("Red car", "Automobile that is red"),                    # парафраз англ
        ("Великий будинок", "Маленький будинок"),                # протилежності укр
    ]
    
    print("\n" + "="*60)
    print("🎯 ТЕСТ МІЖМОВНОЇ ПОДІБНОСТІ")
    print("="*60)
    
    labse_scores = []
    minilm_scores = []
    
    for text1, text2 in test_pairs:
        # LaBSE
        emb1_labse = labse.encode([text1, text2])
        sim_labse = cosine_similarity([emb1_labse[0]], [emb1_labse[1]])[0][0]
        labse_scores.append(sim_labse)
        
        # MiniLM
        emb1_minilm = minilm.encode([text1, text2])
        sim_minilm = cosine_similarity([emb1_minilm[0]], [emb1_minilm[1]])[0][0]
        minilm_scores.append(sim_minilm)
        
        # Визначаємо переможця
        winner = "🏆 LaBSE" if sim_labse > sim_minilm else "🏆 MiniLM" if sim_minilm > sim_labse else "🤝 Нічия"
        diff = abs(sim_labse - sim_minilm)
        
        print(f"\n📝 '{text1}' ↔ '{text2}'")
        print(f"   LaBSE:  {sim_labse:.3f}")
        print(f"   MiniLM: {sim_minilm:.3f}")
        print(f"   {winner} (різниця: {diff:.3f})")
    
    print(f"\n📊 СЕРЕДНІ ПОКАЗНИКИ міжмовної подібності:")
    print(f"   LaBSE:  {np.mean(labse_scores):.3f}")
    print(f"   MiniLM: {np.mean(minilm_scores):.3f}")
    
    # Тест однієї мови
    print("\n" + "="*60)
    print("🏠 ТЕСТ ОДНІЄЇ МОВИ (парафрази)")
    print("="*60)
    
    for text1, text2 in same_language_pairs:
        emb1_labse = labse.encode([text1, text2])
        sim_labse = cosine_similarity([emb1_labse[0]], [emb1_labse[1]])[0][0]
        
        emb1_minilm = minilm.encode([text1, text2])
        sim_minilm = cosine_similarity([emb1_minilm[0]], [emb1_minilm[1]])[0][0]
        
        winner = "🏆 LaBSE" if sim_labse > sim_minilm else "🏆 MiniLM" if sim_minilm > sim_labse else "🤝 Нічия"
        
        print(f"\n📝 '{text1}' ↔ '{text2}'")
        print(f"   LaBSE:  {sim_labse:.3f}")
        print(f"   MiniLM: {sim_minilm:.3f}")
        print(f"   {winner}")
    
    # Тест швидкості
    print("\n" + "="*60)
    print("⚡ ТЕСТ ШВИДКОСТІ")
    print("="*60)
    
    test_texts = [
        "Червоний автомобіль", "Red car", "Красная машина",
        "Синій будинок", "Blue house", "Зелений стіл", "Green table"
    ] * 10  # 70 текстів
    
    # LaBSE швидкість
    start_time = time.time()
    labse_embeddings = labse.encode(test_texts)
    labse_time = time.time() - start_time
    
    # MiniLM швидкість  
    start_time = time.time()
    minilm_embeddings = minilm.encode(test_texts)
    minilm_time = time.time() - start_time
    
    print(f"🐌 LaBSE:  {labse_time:.2f}s ({len(test_texts)} текстів)")
    print(f"⚡ MiniLM: {minilm_time:.2f}s ({len(test_texts)} текстів)")
    print(f"📈 MiniLM швидша в {labse_time/minilm_time:.1f}x разів")
    
    # Розміри векторів
    print(f"\n📐 РОЗМІРИ ВЕКТОРІВ:")
    print(f"   LaBSE:  {labse_embeddings.shape[1]} вимірів")
    print(f"   MiniLM: {minilm_embeddings.shape[1]} вимірів")
    
    # Рекомендації
    print("\n" + "="*60)
    print("💡 РЕКОМЕНДАЦІЇ")
    print("="*60)
    
    avg_labse = np.mean(labse_scores)
    avg_minilm = np.mean(minilm_scores)
    
    if avg_labse > avg_minilm + 0.05:  # суттєва різниця
        print("🎯 Для вашого випадку (укр/рус/англ міжмовний пошук):")
        print("   ✅ Рекомендую LaBSE - значно краща міжмовна подібність")
        print("   ⚠️  Буде повільніша, але точніша для cross-lingual пошуку")
    else:
        print("🤔 Для вашого випадку:")
        print("   ✅ MiniLM може бути достатньою - швидша і компактніша")
        print("   ✅ LaBSE - якщо потрібна максимальна точність міжмовного пошуку")

if __name__ == "__main__":
    compare_models()