#!/usr/bin/env python3
"""
Baseline модель для sanity-check датасета

Сравнение v1.0 vs v1.1 preview:
- TF-IDF + RandomForest/XGBoost
- Multi-output регрессия (Overall, FC, LR, GRA, PR)
- Train/Val split по user_id
- Метрики: MAE, Spearman correlation
"""

import csv
import numpy as np
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from scipy.stats import spearmanr
import re

def load_answers_from_csv(filepath: str):
    """Загружает ответы из CSV"""
    answers = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Пропускаем некорректные строки
                overall = float(row.get('target_band_overall', 0))
                if overall < 3.0 or overall > 9.0:
                    continue
                answers.append(row)
            except:
                continue
    return answers

def extract_handcrafted_features(text: str) -> dict:
    """Извлекает hand-crafted фичи"""
    words = text.split()
    num_words = len(words)
    
    # Filler words
    fillers = ['um', 'uh', 'er', 'erm', 'like', 'you know', 'well', 'actually', 'I mean']
    filler_count = sum(1 for word in words if any(filler in word.lower() for filler in fillers))
    
    # Connectors
    connectors = ['however', 'on the other hand', 'in addition', 'moreover', 'furthermore',
                  'although', 'despite', 'nevertheless', 'also', 'besides']
    connector_count = sum(1 for word in words if any(conn in word.lower() for conn in connectors))
    
    # Repetitions (простое обнаружение)
    unique_words = len(set(word.lower() for word in words))
    repetition_ratio = 1 - (unique_words / num_words) if num_words > 0 else 0
    
    # Punctuation issues
    punctuation_count = text.count('.') + text.count(',') + text.count('!') + text.count('?')
    ellipsis_count = text.count('...')
    
    # Grammar indicators (простое)
    grammar_errors = 0
    # Пропущенные артикли (очень грубо)
    if re.search(r'\bI like \w+$', text, re.IGNORECASE):
        grammar_errors += 1
    # Third person errors
    if re.search(r'\b(he|she|it) (go|do|make|take)\b', text, re.IGNORECASE):
        grammar_errors += 1
    
    return {
        'num_words': num_words,
        'filler_ratio': filler_count / num_words if num_words > 0 else 0,
        'connector_ratio': connector_count / num_words if num_words > 0 else 0,
        'repetition_ratio': repetition_ratio,
        'punctuation_ratio': punctuation_count / num_words if num_words > 0 else 0,
        'ellipsis_ratio': ellipsis_count / num_words if num_words > 0 else 0,
        'grammar_errors': grammar_errors,
    }

def prepare_data(answers, vectorizer=None, fit_vectorizer=True):
    """Подготавливает данные для обучения"""
    texts = []
    handcrafted_features = []
    targets = {
        'overall': [],
        'fc': [],
        'lr': [],
        'gra': [],
        'pr': []
    }
    
    for answer in answers:
        text = answer.get('answer_text', '') or answer.get('transcript_raw', '')
        if not text:
            continue
        
        texts.append(text)
        handcrafted_features.append(extract_handcrafted_features(text))
        
        try:
            targets['overall'].append(float(answer['target_band_overall']))
            targets['fc'].append(float(answer['target_band_fc']))
            targets['lr'].append(float(answer['target_band_lr']))
            targets['gra'].append(float(answer['target_band_gra']))
            targets['pr'].append(float(answer['target_band_pr']))
        except:
            continue
    
    # TF-IDF
    if fit_vectorizer:
        vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2), min_df=2)
        tfidf_features = vectorizer.fit_transform(texts)
    else:
        tfidf_features = vectorizer.transform(texts)
    
    # Hand-crafted features
    hc_array = np.array([
        [hc['num_words'], hc['filler_ratio'], hc['connector_ratio'],
         hc['repetition_ratio'], hc['punctuation_ratio'], hc['ellipsis_ratio'],
         hc['grammar_errors']]
        for hc in handcrafted_features
    ])
    
    # Объединяем фичи
    from scipy.sparse import hstack
    X = hstack([tfidf_features, hc_array])
    
    y = np.array([targets['overall'], targets['fc'], targets['lr'], 
                  targets['gra'], targets['pr']]).T
    
    return X, y, vectorizer

def split_by_user(answers):
    """Разделяет на train/val по user_id"""
    users = defaultdict(list)
    for answer in answers:
        user_id = answer.get('user_id', '')
        if user_id:
            users[user_id].append(answer)
    
    user_ids = list(users.keys())
    np.random.seed(42)
    np.random.shuffle(user_ids)
    
    split_idx = int(len(user_ids) * 0.8)
    train_users = set(user_ids[:split_idx])
    val_users = set(user_ids[split_idx:])
    
    train_answers = [a for a in answers if a.get('user_id', '') in train_users]
    val_answers = [a for a in answers if a.get('user_id', '') in val_users]
    
    return train_answers, val_answers

def evaluate_model(y_true, y_pred, metric_name="MAE"):
    """Оценивает модель"""
    results = {}
    
    criteria = ['overall', 'fc', 'lr', 'gra', 'pr']
    
    for i, criterion in enumerate(criteria):
        true_vals = y_true[:, i]
        pred_vals = y_pred[:, i]
        
        if metric_name == "MAE":
            score = mean_absolute_error(true_vals, pred_vals)
        elif metric_name == "RMSE":
            score = np.sqrt(mean_squared_error(true_vals, pred_vals))
        elif metric_name == "Spearman":
            corr, _ = spearmanr(true_vals, pred_vals)
            score = corr if not np.isnan(corr) else 0.0
        
        results[criterion] = score
    
    return results

def evaluate_by_band_range(y_true, y_pred):
    """Оценивает ошибки по диапазонам band scores"""
    overall_true = y_true[:, 0]
    overall_pred = y_pred[:, 0]
    
    ranges = {
        'low (≤5.0)': (overall_true <= 5.0),
        'medium (5.5-6.5)': (overall_true >= 5.5) & (overall_true <= 6.5),
        'high (≥7.0)': (overall_true >= 7.0),
    }
    
    results = {}
    for range_name, mask in ranges.items():
        if np.sum(mask) > 0:
            mae = mean_absolute_error(overall_true[mask], overall_pred[mask])
            results[range_name] = {
                'mae': mae,
                'count': np.sum(mask)
            }
    
    return results

def main():
    print("=" * 70)
    print("BASELINE МОДЕЛЬ: СРАВНЕНИЕ V1.0 VS V1.1 PREVIEW")
    print("=" * 70)
    
    # Загружаем v1.0
    print("\n📂 Загрузка v1.0...")
    v1_0_answers = load_answers_from_csv('dataset_versions/v1.0/answers.csv')
    print(f"   Загружено: {len(v1_0_answers)} ответов")
    
    # Загружаем mini-v1.1
    print("\n📂 Загрузка mini-v1.1...")
    try:
        v1_1_preview = load_answers_from_csv('answers_mini_v1.1.csv')
        print(f"   Загружено: {len(v1_1_preview)} ответов")
    except FileNotFoundError:
        print("   ⚠️  Файл answers_mini_v1.1.csv не найден")
        v1_1_preview = []
    
    if not v1_1_preview:
        print("\n⚠️  Preview не найден, работаем только с v1.0")
        all_answers = v1_0_answers
    else:
        # Объединяем для обучения
        all_answers = v1_0_answers + v1_1_preview
        print(f"\n📊 Всего ответов для обучения: {len(all_answers)}")
    
    # Split по user_id
    print("\n🔄 Разделение на train/val по user_id...")
    train_answers, val_answers = split_by_user(all_answers)
    print(f"   Train: {len(train_answers)} ответов")
    print(f"   Val: {len(val_answers)} ответов")
    
    # Подготовка данных
    print("\n🔧 Подготовка данных...")
    X_train, y_train, vectorizer = prepare_data(train_answers, fit_vectorizer=True)
    X_val, y_val, _ = prepare_data(val_answers, vectorizer=vectorizer, fit_vectorizer=False)
    
    print(f"   Train features shape: {X_train.shape}")
    print(f"   Val features shape: {X_val.shape}")
    
    # Обучение модели
    print("\n🤖 Обучение модели (RandomForest, multi-output)...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Предсказания
    print("\n📊 Предсказания...")
    y_pred_train = model.predict(X_train)
    y_pred_val = model.predict(X_val)
    
    # Метрики
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 70)
    
    print("\n📈 MAE (Mean Absolute Error):")
    print("\n   Train:")
    train_mae = evaluate_model(y_train, y_pred_train, "MAE")
    for criterion, mae in train_mae.items():
        print(f"      {criterion.upper()}: {mae:.3f}")
    
    print("\n   Validation:")
    val_mae = evaluate_model(y_val, y_pred_val, "MAE")
    for criterion, mae in val_mae.items():
        print(f"      {criterion.upper()}: {mae:.3f}")
    
    print("\n📊 Spearman Correlation:")
    val_spearman = evaluate_model(y_val, y_pred_val, "Spearman")
    for criterion, corr in val_spearman.items():
        print(f"      {criterion.upper()}: {corr:.3f}")
    
    print("\n🎯 Ошибки по диапазонам (Overall):")
    val_by_range = evaluate_by_band_range(y_val, y_pred_val)
    for range_name, metrics in val_by_range.items():
        print(f"      {range_name}: MAE={metrics['mae']:.3f} (n={metrics['count']})")
    
    # Feature importance (если доступно)
    if hasattr(model, 'feature_importances_'):
        print("\n🔍 Top 10 важных фичей (hand-crafted):")
        # Берем последние 7 фичей (hand-crafted)
        hc_importance = model.feature_importances_[-7:]
        hc_names = ['num_words', 'filler_ratio', 'connector_ratio', 'repetition_ratio',
                   'punctuation_ratio', 'ellipsis_ratio', 'grammar_errors']
        importance_pairs = list(zip(hc_names, hc_importance))
        importance_pairs.sort(key=lambda x: x[1], reverse=True)
        for name, importance in importance_pairs[:10]:
            print(f"      {name}: {importance:.4f}")
    
    print("\n" + "=" * 70)
    print("✅ Baseline модель обучена и оценена")
    print("=" * 70)
    
    # Сохраняем результаты (конвертируем numpy типы в Python типы)
    def convert_to_python(obj):
        if isinstance(obj, dict):
            return {k: convert_to_python(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_to_python(item) for item in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
    
    results = {
        'train_mae': train_mae,
        'val_mae': val_mae,
        'val_spearman': val_spearman,
        'val_by_range': {k: {k2: convert_to_python(v2) for k2, v2 in v.items()} for k, v in val_by_range.items()},
    }
    
    results = convert_to_python(results)
    
    import json
    with open('baseline_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n💾 Результаты сохранены в baseline_results.json")

if __name__ == '__main__':
    main()

