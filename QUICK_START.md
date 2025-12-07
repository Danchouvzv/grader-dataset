# 🚀 Быстрый старт: Обучение модели

## 📊 Что у тебя есть

### Датасет v1.3 (готов к обучению)

**Файлы:**
- ✅ `dataset_versions/v1.3/train.csv` - **3376 ответов** (для обучения)
- ✅ `dataset_versions/v1.3/val.csv` - **398 ответов** (для валидации)
- ✅ `dataset_versions/v1.3/test.csv` - **490 ответов** (для финального теста)

**Что внутри:**
- Part 1: 38.7% / Part 2: 28.8% / Part 3: 32.5%
- Low (≤5.5): 39% / Mid (6.0-6.5): 30% / High (≥7.0): 31%
- Sample weights: 430 ответов с весом 0.4-0.6 (inconsistent)

## 🎯 Что предсказывать

**Основная задача:**
- `target_band_overall` - общий балл (регрессия, 0.5-band шкала)

**Дополнительно (multi-task):**
- `target_band_fc` - Fluency & Coherence
- `target_band_lr` - Lexical Resource
- `target_band_gra` - Grammatical Range & Accuracy
- `target_band_pr` - Pronunciation

## 📝 Как обучать

### Вариант 1: Baseline (TF-IDF + LightGBM) - 5 минут

```python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error
import numpy as np

# Загрузка данных
train = pd.read_csv('dataset_versions/v1.3/train.csv')
val = pd.read_csv('dataset_versions/v1.3/val.csv')

# Подготовка текста
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_train = vectorizer.fit_transform(train['answer_text'])
X_val = vectorizer.transform(val['answer_text'])

# Targets
y_train = train[['target_band_overall', 'target_band_fc', 
                 'target_band_lr', 'target_band_gra', 'target_band_pr']].values
y_val = val[['target_band_overall', 'target_band_fc', 
             'target_band_lr', 'target_band_gra', 'target_band_pr']].values

# Sample weights
weights = train['sample_weight'].astype(float).values

# Обучение
model = MultiOutputRegressor(LGBMRegressor(n_estimators=100, random_state=42))
model.fit(X_train, y_train, sample_weight=weights)

# Предсказания
pred = model.predict(X_val)

# Метрики
mae_overall = mean_absolute_error(y_val[:, 0], pred[:, 0])
print(f"MAE Overall: {mae_overall:.3f}")

# Калибровка (округление до 0.5)
pred_rounded = np.round(pred * 2) / 2
accuracy_05 = np.mean(np.abs(pred_rounded[:, 0] - y_val[:, 0]) <= 0.5)
print(f"Accuracy within ±0.5: {accuracy_05:.2%}")
```

### Вариант 2: Encoder (DistilBERT) - 30 минут на GPU

```python
from transformers import DistilBERTTokenizer, DistilBERTForSequenceClassification
from transformers import Trainer, TrainingArguments
import torch
from torch.utils.data import Dataset
import pandas as pd

# Загрузка данных
train = pd.read_csv('dataset_versions/v1.3/train.csv')
val = pd.read_csv('dataset_versions/v1.3/val.csv')

# Dataset class
class IELTSDataset(Dataset):
    def __init__(self, texts, labels, weights=None):
        self.texts = texts
        self.labels = labels
        self.weights = weights if weights is not None else [1.0] * len(texts)
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        return {
            'text': self.texts[idx],
            'labels': self.labels[idx],
            'weight': self.weights[idx]
        }

# Подготовка
tokenizer = DistilBERTTokenizer.from_pretrained('distilbert-base-uncased')
train_texts = train['answer_text'].tolist()
train_labels = train[['target_band_overall']].values
train_weights = train['sample_weight'].astype(float).values

# Токенизация
train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=512)

# Обучение (упрощенный пример)
# Полный код см. в docs/TRAINING_GUIDE_V1.3.md
```

## 📈 Метрики для оценки

**Обязательные:**
- MAE (Mean Absolute Error) по `target_band_overall`
- Accuracy within ±0.5 band (после калибровки)

**Дополнительно:**
- MAE по каждому subscore (FC, LR, GRA, PR)
- Метрики по частям (Part 1, 2, 3 отдельно)
- Метрики по бэндам (low, mid, high отдельно)

## ⚠️ Важно

1. **Используй sample weights** - 430 ответов имеют вес 0.4-0.6
2. **Калибруй предсказания** - округляй до 0.5-band (`round(pred * 2) / 2`)
3. **Тестируй на test.csv** только в конце, не подглядывай!

## 📚 Полная документация

- `docs/TRAINING_GUIDE_V1.3.md` - детальное руководство
- `docs/TRAINING_PLAN.md` - план обучения
- `configs/training_config_v1.3.json` - конфигурация

## 🎯 Ожидаемые результаты

**Baseline (TF-IDF + LightGBM):**
- MAE: ~0.4-0.5
- Accuracy ±0.5: ~60-70%

**Encoder (DistilBERT):**
- MAE: ~0.3-0.4
- Accuracy ±0.5: ~70-80%

**Multi-task (с subscores):**
- MAE Overall: ~0.35-0.45
- MAE Subscores: ~0.5-0.6

