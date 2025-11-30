from sklearn.metrics import precision_recall_fscore_support
import numpy as np

# Припустимо, у тебе є:
# texts = [...]            # список новин
# true_labels = [...]      # 1 = discard, 0 = keep

thresholds = np.arange(0.1, 0.95, 0.05)
best_f1 = 0
best_threshold = 0.5

for t in thresholds:
    predictions = []
    for text in texts:
        result = classifier(text, candidate_labels, multi_class=True)
        max_score = max(result["scores"])
        pred = 1 if max_score > t else 0  # 1 = discard
        predictions.append(pred)
    
    precision, recall, f1, _ = precision_recall_fscore_support(
        true_labels, predictions, average='binary', zero_division=0
    )
    
    if f1 > best_f1:
        best_f1 = f1
        best_threshold = t

print(f"Найкращий поріг: {best_threshold:.2f} (F1 = {best_f1:.3f})")