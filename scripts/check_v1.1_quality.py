#!/usr/bin/env python3
"""
Проверка качества v1.1: сравнение с v1.0 через baseline модель
"""

import csv
import sys
from baseline_model import load_answers_from_csv, prepare_data, split_by_user, evaluate_model, evaluate_by_band_range
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
import numpy as np

def main():
    print("=" * 70)
    print("ПРОВЕРКА КАЧЕСТВА V1.1")
    print("=" * 70)
    
    # Загружаем v1.0
    print("\n📂 Загрузка v1.0...")
    v1_0 = load_answers_from_csv('dataset_versions/v1.0/answers.csv')
    print(f"   Загружено: {len(v1_0)} ответов")
    
    # Загружаем v1.1
    print("\n📂 Загрузка v1.1...")
    try:
        v1_1 = load_answers_from_csv('dataset_versions/v1.1/answers.csv')
        print(f"   Загружено: {len(v1_1)} ответов")
    except Exception as e:
        print(f"   ❌ Ошибка загрузки: {e}")
        print("   Попробуй проверить файл вручную")
        return
    
    # Обучаем на v1.0
    print("\n🤖 Обучение baseline на v1.0...")
    train_v1_0, val_v1_0 = split_by_user(v1_0)
    X_train, y_train, vectorizer = prepare_data(train_v1_0, fit_vectorizer=True)
    X_val, y_val, _ = prepare_data(val_v1_0, vectorizer=vectorizer, fit_vectorizer=False)
    
    model = RandomForestRegressor(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    y_pred_v1_0 = model.predict(X_val)
    mae_v1_0 = evaluate_model(y_val, y_pred_v1_0, "MAE")
    
    print(f"   MAE на v1.0 validation: {mae_v1_0['overall']:.3f}")
    
    # Тестируем на v1.1 (только новые данные)
    print("\n📊 Тестирование на новых данных v1.1...")
    v1_1_new = [a for a in v1_1 if a.get('source_type') == 'synthetic_v1.1']
    print(f"   Новых ответов v1.1: {len(v1_1_new)}")
    
    if len(v1_1_new) > 0:
        X_v1_1, y_v1_1, _ = prepare_data(v1_1_new, vectorizer=vectorizer, fit_vectorizer=False)
        y_pred_v1_1 = model.predict(X_v1_1)
        mae_v1_1 = evaluate_model(y_v1_1, y_pred_v1_1, "MAE")
        
        print(f"   MAE на новых v1.1: {mae_v1_1['overall']:.3f}")
        print(f"   Разница: {mae_v1_1['overall'] - mae_v1_0['overall']:+.3f}")
        
        if mae_v1_1['overall'] <= mae_v1_0['overall'] * 1.1:
            print("   ✅ Качество приемлемое (в пределах 10% от baseline)")
        else:
            print("   ⚠️  Качество хуже baseline - возможно нужны доработки")
    
    print("\n✅ Проверка завершена")

if __name__ == '__main__':
    main()

