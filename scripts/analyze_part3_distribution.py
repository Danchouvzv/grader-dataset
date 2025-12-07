#!/usr/bin/env python3
"""
Анализ распределения Part 3 по бэндам
Проверка дисбаланса для выявления проблем
"""

import csv
from collections import Counter

def analyze_distribution(filepath: str):
    """Анализирует распределение Part 3 по бэндам"""
    print("=" * 70)
    print("АНАЛИЗ РАСПРЕДЕЛЕНИЯ PART 3 ПО БЭНДАМ")
    print("=" * 70)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        answers = list(csv.DictReader(f))
    
    # Фильтруем Part 3
    part3 = [a for a in answers if a['part'] == '3']
    print(f"\n📊 Всего Part 3 ответов: {len(part3)}")
    
    # Распределение по overall
    overall_scores = []
    for a in part3:
        try:
            score = float(a['target_band_overall'])
            overall_scores.append(score)
        except:
            continue
    
    # Группируем по диапазонам
    ranges = {
        'Very Low (3.0-4.0)': [],
        'Low (4.5-5.0)': [],
        'Mid-Low (5.5-6.0)': [],
        'Mid-High (6.5-7.0)': [],
        'High (7.5-8.0)': [],
        'Very High (8.5-9.0)': []
    }
    
    for score in overall_scores:
        if 3.0 <= score <= 4.0:
            ranges['Very Low (3.0-4.0)'].append(score)
        elif 4.5 <= score <= 5.0:
            ranges['Low (4.5-5.0)'].append(score)
        elif 5.5 <= score <= 6.0:
            ranges['Mid-Low (5.5-6.0)'].append(score)
        elif 6.5 <= score <= 7.0:
            ranges['Mid-High (6.5-7.0)'].append(score)
        elif 7.5 <= score <= 8.0:
            ranges['High (7.5-8.0)'].append(score)
        elif 8.5 <= score <= 9.0:
            ranges['Very High (8.5-9.0)'].append(score)
    
    print("\n📈 Распределение по диапазонам:")
    print(f"{'Диапазон':<25} {'Количество':<15} {'Процент':<10}")
    print("-" * 50)
    
    total = len(overall_scores)
    for range_name, scores in ranges.items():
        count = len(scores)
        percentage = (count / total * 100) if total > 0 else 0
        print(f"{range_name:<25} {count:<15} {percentage:>6.1f}%")
    
    # Детальное распределение по каждому бэнду
    print("\n📊 Детальное распределение:")
    band_counts = Counter(overall_scores)
    for band in sorted(band_counts.keys()):
        count = band_counts[band]
        percentage = (count / total * 100) if total > 0 else 0
        bar = "█" * int(percentage / 2)
        print(f"   {band:>4.1f}: {count:>4} ({percentage:>5.1f}%) {bar}")
    
    # Проверка дисбаланса
    print("\n⚠️  ПРОВЕРКА ДИСБАЛАНСА:")
    
    low_mid = len(ranges['Very Low (3.0-4.0)']) + len(ranges['Low (4.5-5.0)']) + len(ranges['Mid-Low (5.5-6.0)'])
    high = len(ranges['Mid-High (6.5-7.0)']) + len(ranges['High (7.5-8.0)']) + len(ranges['Very High (8.5-9.0)'])
    
    low_pct = (low_mid / total * 100) if total > 0 else 0
    high_pct = (high / total * 100) if total > 0 else 0
    
    print(f"   Low-Mid (≤6.0): {low_mid} ({low_pct:.1f}%)")
    print(f"   High (≥6.5): {high} ({high_pct:.1f}%)")
    
    if high_pct > 70:
        print("   ⚠️  ПРОБЛЕМА: Слишком много высоких бэндов (>70%)")
        print("      Модель будет переоценивать слабых кандидатов")
    elif low_pct < 20:
        print("   ⚠️  ПРОБЛЕМА: Слишком мало низких бэндов (<20%)")
        print("      Модель плохо различает слабых кандидатов")
    else:
        print("   ✅ Распределение выглядит сбалансированным")

if __name__ == '__main__':
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'dataset_versions/v1.2/answers.csv'
    analyze_distribution(filepath)

