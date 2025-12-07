# 🚀 Полная инструкция: Обучение модели в Google Colab

**Для новичков - пошагово, с нуля**

---

## 📋 Что нужно перед началом

1. Аккаунт Google (для доступа к Colab)
2. Репозиторий на GitHub: https://github.com/Danchouvzv/grader-dataset
3. 30-60 минут времени

---

## 🎯 Шаг 1: Открыть Google Colab

1. Перейди на https://colab.research.google.com/
2. Нажми **"New notebook"** (или **"Файл" → "Новый блокнот"**)
3. Переименуй блокнот: нажми на "Untitled0" вверху → введи "IELTS Model Training"

---

## 📥 Шаг 2: Загрузить датасет из GitHub

**Скопируй и выполни этот код в первой ячейке:**

```python
# Установка git (если нужно)
!apt-get update
!apt-get install -y git

# Клонирование репозитория
!git clone https://github.com/Danchouvzv/grader-dataset.git

# Переход в папку проекта
import os
os.chdir('/content/grader-dataset')

# Проверка, что файлы загрузились
!ls -la dataset_versions/v1.1/
```

**Что произошло:**
- Репозиторий склонирован в `/content/grader-dataset`
- Датасет находится в `dataset_versions/v1.1/`

---

## 📦 Шаг 3: Установить зависимости

**Создай новую ячейку и выполни:**

```python
# Установка всех необходимых библиотек
!pip install torch transformers scikit-learn pandas numpy matplotlib tqdm

# Проверка установки
import torch
print(f"PyTorch версия: {torch.__version__}")
print(f"CUDA доступна: {torch.cuda.is_available()}")  # Должно быть True для GPU
```

**Важно:** 
- Colab автоматически даёт GPU (бесплатно)
- Если `CUDA доступна: True` → будет быстро (20-30 минут)
- Если `False` → будет медленно (2-3 часа), но тоже работает

---

## 🔧 Шаг 4: Подготовить скрипт обучения

**Создай новую ячейку и скопируй весь этот код:**

```python
# Создаём файл train_model.py прямо в Colab
%%writefile train_model_colab.py

#!/usr/bin/env python3
"""
Обучение модели для оценки IELTS Speaking в Google Colab
"""

import csv
import json
import numpy as np
from collections import defaultdict
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from scipy.stats import spearmanr
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Конфигурация
CONFIG = {
    'model_name': 'distilbert-base-uncased',  # Легче и быстрее чем BERT
    'max_length': 256,
    'batch_size': 16,
    'learning_rate': 2e-5,
    'epochs': 5,
    'device': 'cuda' if torch.cuda.is_available() else 'cpu',
    'random_seed': 42
}

class IELTSDataset(Dataset):
    """Dataset для IELTS ответов"""
    def __init__(self, texts, targets, tokenizer, max_length=256):
        self.texts = texts
        self.targets = targets
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        target = self.targets[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'targets': torch.FloatTensor(target)
        }

class IELTSModel(nn.Module):
    """Модель для предсказания 5 субскоров"""
    def __init__(self, model_name, num_outputs=5):
        super(IELTSModel, self).__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.3)
        
        # Multi-head для каждого субскора
        self.fc_overall = nn.Linear(self.encoder.config.hidden_size, 1)
        self.fc_fc = nn.Linear(self.encoder.config.hidden_size, 1)
        self.fc_lr = nn.Linear(self.encoder.config.hidden_size, 1)
        self.fc_gra = nn.Linear(self.encoder.config.hidden_size, 1)
        self.fc_pr = nn.Linear(self.encoder.config.hidden_size, 1)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        
        overall = self.fc_overall(pooled_output)
        fc = self.fc_fc(pooled_output)
        lr = self.fc_lr(pooled_output)
        gra = self.fc_gra(pooled_output)
        pr = self.fc_pr(pooled_output)
        
        return torch.cat([overall, fc, lr, gra, pr], dim=1)

def load_data(filepath):
    """Загружает данные из CSV"""
    texts = []
    targets = []
    user_ids = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                text = row.get('answer_text', '') or row.get('transcript_raw', '')
                if not text or len(text) < 5:
                    continue
                
                overall = float(row['target_band_overall'])
                fc = float(row['target_band_fc'])
                lr = float(row['target_band_lr'])
                gra = float(row['target_band_gra'])
                pr = float(row['target_band_pr'])
                
                # Фильтруем некорректные значения
                if not (3.0 <= overall <= 9.0):
                    continue
                
                texts.append(text)
                targets.append([overall, fc, lr, gra, pr])
                user_ids.append(row.get('user_id', ''))
            except:
                continue
    
    return texts, np.array(targets), user_ids

def split_by_user(texts, targets, user_ids, test_size=0.2):
    """Разделяет данные по user_id"""
    user_to_indices = defaultdict(list)
    for i, uid in enumerate(user_ids):
        user_to_indices[uid].append(i)
    
    users = list(user_to_indices.keys())
    train_users, val_users = train_test_split(users, test_size=test_size, random_state=42)
    
    train_indices = []
    val_indices = []
    
    for uid in train_users:
        train_indices.extend(user_to_indices[uid])
    for uid in val_users:
        val_indices.extend(user_to_indices[uid])
    
    return (np.array(texts)[train_indices], targets[train_indices],
            np.array(texts)[val_indices], targets[val_indices])

def train_epoch(model, dataloader, optimizer, criterion, device):
    """Одна эпоха обучения"""
    model.train()
    total_loss = 0
    
    for batch in tqdm(dataloader, desc="Training"):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        targets = batch['targets'].to(device)
        
        optimizer.zero_grad()
        outputs = model(input_ids, attention_mask)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(dataloader)

def evaluate(model, dataloader, criterion, device):
    """Оценка модели"""
    model.eval()
    total_loss = 0
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            targets = batch['targets'].to(device)
            
            outputs = model(input_ids, attention_mask)
            loss = criterion(outputs, targets)
            
            total_loss += loss.item()
            all_preds.append(outputs.cpu().numpy())
            all_targets.append(targets.cpu().numpy())
    
    all_preds = np.vstack(all_preds)
    all_targets = np.vstack(all_targets)
    
    # Метрики
    mae = mean_absolute_error(all_targets, all_preds, multioutput='raw_values')
    mse = mean_squared_error(all_targets, all_preds, multioutput='raw_values')
    rmse = np.sqrt(mse)
    
    # Spearman correlation
    correlations = []
    for i in range(5):
        corr, _ = spearmanr(all_targets[:, i], all_preds[:, i])
        correlations.append(corr if not np.isnan(corr) else 0.0)
    
    return {
        'loss': total_loss / len(dataloader),
        'mae': mae,
        'rmse': rmse,
        'correlations': correlations
    }

def main():
    print("=" * 70)
    print("ОБУЧЕНИЕ IELTS SPEAKING МОДЕЛИ")
    print("=" * 70)
    
    print(f"\n🔧 Конфигурация:")
    print(f"   Модель: {CONFIG['model_name']}")
    print(f"   Устройство: {CONFIG['device']}")
    print(f"   Batch size: {CONFIG['batch_size']}")
    print(f"   Epochs: {CONFIG['epochs']}")
    
    # Загрузка данных
    print(f"\n📂 Загрузка данных...")
    texts, targets, user_ids = load_data('dataset_versions/v1.1/answers.csv')
    print(f"   Загружено: {len(texts)} ответов")
    
    # Split по user_id
    print(f"\n🔄 Разделение на train/val по user_id...")
    train_texts, train_targets, val_texts, val_targets = split_by_user(texts, targets, user_ids)
    print(f"   Train: {len(train_texts)} ответов")
    print(f"   Val: {len(val_texts)} ответов")
    
    # Токенизатор и модель
    print(f"\n🤖 Загрузка модели {CONFIG['model_name']}...")
    tokenizer = AutoTokenizer.from_pretrained(CONFIG['model_name'])
    model = IELTSModel(CONFIG['model_name']).to(CONFIG['device'])
    
    # Datasets и DataLoaders
    train_dataset = IELTSDataset(train_texts, train_targets, tokenizer, CONFIG['max_length'])
    val_dataset = IELTSDataset(val_texts, val_targets, tokenizer, CONFIG['max_length'])
    
    train_loader = DataLoader(train_dataset, batch_size=CONFIG['batch_size'], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=CONFIG['batch_size'], shuffle=False)
    
    # Оптимизатор и loss
    optimizer = torch.optim.AdamW(model.parameters(), lr=CONFIG['learning_rate'])
    criterion = nn.MSELoss()
    
    # Обучение
    print(f"\n🚀 Начало обучения...")
    best_val_loss = float('inf')
    history = {'train_loss': [], 'val_loss': [], 'val_mae': []}
    
    for epoch in range(CONFIG['epochs']):
        print(f"\n📊 Epoch {epoch + 1}/{CONFIG['epochs']}")
        
        # Train
        train_loss = train_epoch(model, train_loader, optimizer, criterion, CONFIG['device'])
        history['train_loss'].append(train_loss)
        
        # Val
        val_metrics = evaluate(model, val_loader, criterion, CONFIG['device'])
        history['val_loss'].append(val_metrics['loss'])
        history['val_mae'].append(val_metrics['mae'])
        
        print(f"\n   Train Loss: {train_loss:.4f}")
        print(f"   Val Loss: {val_metrics['loss']:.4f}")
        print(f"   Val MAE:")
        print(f"      Overall: {val_metrics['mae'][0]:.3f}")
        print(f"      FC: {val_metrics['mae'][1]:.3f}")
        print(f"      LR: {val_metrics['mae'][2]:.3f}")
        print(f"      GRA: {val_metrics['mae'][3]:.3f}")
        print(f"      PR: {val_metrics['mae'][4]:.3f}")
        print(f"   Val Correlations:")
        print(f"      Overall: {val_metrics['correlations'][0]:.3f}")
        print(f"      FC: {val_metrics['correlations'][1]:.3f}")
        print(f"      LR: {val_metrics['correlations'][2]:.3f}")
        print(f"      GRA: {val_metrics['correlations'][3]:.3f}")
        print(f"      PR: {val_metrics['correlations'][4]:.3f}")
        
        # Сохраняем лучшую модель
        if val_metrics['loss'] < best_val_loss:
            best_val_loss = val_metrics['loss']
            torch.save(model.state_dict(), 'models/ielts_model_best.pt')
            print(f"   ✅ Сохранена лучшая модель (loss: {best_val_loss:.4f})")
    
    # Финальная оценка
    print(f"\n" + "=" * 70)
    print("ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 70)
    
    model.load_state_dict(torch.load('models/ielts_model_best.pt'))
    final_metrics = evaluate(model, val_loader, criterion, CONFIG['device'])
    
    print(f"\n📊 Лучшая модель на Validation:")
    print(f"   MAE Overall: {final_metrics['mae'][0]:.3f}")
    print(f"   Spearman Overall: {final_metrics['correlations'][0]:.3f}")
    
    # Сохраняем результаты
    results = {
        'config': CONFIG,
        'final_metrics': {
            'mae': final_metrics['mae'].tolist(),
            'correlations': final_metrics['correlations'],
            'rmse': final_metrics['rmse'].tolist()
        },
        'history': history
    }
    
    import os
    os.makedirs('models', exist_ok=True)
    with open('models/training_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Модель сохранена в models/ielts_model_best.pt")
    print(f"💾 Результаты сохранены в models/training_results.json")
    print(f"\n✅ Обучение завершено!")

if __name__ == '__main__':
    import os
    os.makedirs('models', exist_ok=True)
    main()
```

**Что это делает:**
- Создаёт файл `train_model_colab.py` с полным кодом обучения
- Всё готово к запуску

---

## 🚀 Шаг 5: Запустить обучение

**Создай новую ячейку и выполни:**

```python
# Создаём папку для моделей
import os
os.makedirs('models', exist_ok=True)

# Запускаем обучение
!python train_model_colab.py
```

**Что будет происходить:**
1. Загрузка данных (4022 ответа)
2. Разделение на train/val (80/20)
3. Загрузка DistilBERT модели
4. Обучение 5 эпох
5. Сохранение лучшей модели

**Время:**
- С GPU: ~20-30 минут
- Без GPU: ~2-3 часа

---

## 📊 Шаг 6: Посмотреть результаты

**После обучения выполни:**

```python
# Загружаем результаты
import json
with open('models/training_results.json', 'r') as f:
    results = json.load(f)

print("=" * 70)
print("РЕЗУЛЬТАТЫ ОБУЧЕНИЯ")
print("=" * 70)

metrics = results['final_metrics']
print(f"\n📊 MAE (Mean Absolute Error):")
print(f"   Overall: {metrics['mae'][0]:.3f}")
print(f"   FC: {metrics['mae'][1]:.3f}")
print(f"   LR: {metrics['mae'][2]:.3f}")
print(f"   GRA: {metrics['mae'][3]:.3f}")
print(f"   PR: {metrics['mae'][4]:.3f}")

print(f"\n📈 Spearman Correlation:")
print(f"   Overall: {metrics['correlations'][0]:.3f}")
print(f"   FC: {metrics['correlations'][1]:.3f}")
print(f"   LR: {metrics['correlations'][2]:.3f}")
print(f"   GRA: {metrics['correlations'][3]:.3f}")
print(f"   PR: {metrics['correlations'][4]:.3f}")
```

---

## 💾 Шаг 7: Скачать модель

**Чтобы скачать обученную модель на компьютер:**

```python
# Скачиваем модель
from google.colab import files

# Скачиваем файл модели
files.download('models/ielts_model_best.pt')

# Скачиваем результаты
files.download('models/training_results.json')
```

**Или через интерфейс:**
1. В левой панели нажми на иконку папки 📁
2. Найди `models/ielts_model_best.pt`
3. Правый клик → "Download"

---

## 🎯 Шаг 8: Использовать модель для предсказаний

**Создай новую ячейку для тестирования:**

```python
# Загрузка обученной модели
import torch
from transformers import AutoTokenizer, AutoModel
import torch.nn as nn

# Класс модели (скопируй из train_model_colab.py)
class IELTSModel(nn.Module):
    def __init__(self, model_name):
        super(IELTSModel, self).__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.3)
        self.fc_overall = nn.Linear(self.encoder.config.hidden_size, 1)
        self.fc_fc = nn.Linear(self.encoder.config.hidden_size, 1)
        self.fc_lr = nn.Linear(self.encoder.config.hidden_size, 1)
        self.fc_gra = nn.Linear(self.encoder.config.hidden_size, 1)
        self.fc_pr = nn.Linear(self.encoder.config.hidden_size, 1)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        overall = self.fc_overall(pooled_output)
        fc = self.fc_fc(pooled_output)
        lr = self.fc_lr(pooled_output)
        gra = self.fc_gra(pooled_output)
        pr = self.fc_pr(pooled_output)
        return torch.cat([overall, fc, lr, gra, pr], dim=1)

# Загрузка модели
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_name = 'distilbert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = IELTSModel(model_name).to(device)
model.load_state_dict(torch.load('models/ielts_model_best.pt'))
model.eval()

# Пример предсказания
def predict(text):
    encoding = tokenizer(
        text,
        truncation=True,
        padding='max_length',
        max_length=256,
        return_tensors='pt'
    )
    
    with torch.no_grad():
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)
        outputs = model(input_ids, attention_mask)
    
    scores = outputs[0].cpu().numpy()
    return {
        'Overall': round(scores[0], 1),
        'FC': round(scores[1], 1),
        'LR': round(scores[2], 1),
        'GRA': round(scores[3], 1),
        'PR': round(scores[4], 1)
    }

# Тестируем на примере
test_text = "I really enjoy reading books in my free time. I find it quite relaxing and it helps me unwind after a busy day."
result = predict(test_text)

print("Предсказанные оценки:")
for criterion, score in result.items():
    print(f"   {criterion}: {score}")
```

---

## ⚠️ Важные замечания

### Если Colab отключился во время обучения:

1. **Сессия Colab может отключиться через 90 минут неактивности**
2. **Решение:** Периодически двигай мышкой или добавляй ячейки с `print("still running")`

### Если не хватает памяти:

```python
# Уменьши batch_size в CONFIG
CONFIG['batch_size'] = 8  # Вместо 16
```

### Если обучение идёт медленно:

1. Проверь, что GPU включен: **Runtime → Change runtime type → GPU**
2. Если GPU нет → будет долго, но работает

---

## 📝 Чеклист для новичка

- [ ] Открыл Google Colab
- [ ] Склонировал репозиторий (Шаг 2)
- [ ] Установил зависимости (Шаг 3)
- [ ] Создал train_model_colab.py (Шаг 4)
- [ ] Запустил обучение (Шаг 5)
- [ ] Дождался завершения (20-30 минут)
- [ ] Посмотрел результаты (Шаг 6)
- [ ] Скачал модель (Шаг 7)

---

## 🆘 Если что-то пошло не так

### Ошибка "No module named 'transformers'"
→ Выполни снова: `!pip install transformers`

### Ошибка "CUDA out of memory"
→ Уменьши batch_size до 8 или 4

### Ошибка "File not found"
→ Проверь, что ты в правильной папке: `!pwd` должно показать `/content/grader-dataset`

---

**Готово! Теперь у тебя есть обученная модель для оценки IELTS Speaking! 🎉**

