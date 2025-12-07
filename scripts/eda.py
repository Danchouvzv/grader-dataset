#!/usr/bin/env python3
"""
EDA (Exploratory Data Analysis) для датасета IELTS.
Создает гистограммы и статистику.
"""

import csv
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict, Counter

def load_data():
    """Загружает данные из CSV"""
    answers = []
    with open('answers.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            answers.append(row)
    
    users = {}
    with open('users.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            users[row['user_id']] = float(row['level_estimate']) if row['level_estimate'] else None
    
    return answers, users

def analyze_dataset():
    """Основной анализ датасета"""
    answers, users = load_data()
    
    print("=" * 60)
    print("IELTS DATASET EDA")
    print("=" * 60)
    
    # 1. Общая статистика
    print(f"\n📊 Общая статистика:")
    print(f"  Всего ответов: {len(answers)}")
    print(f"  Всего пользователей: {len(users)}")
    
    # 2. Распределение по частям
    parts = Counter([a['part'] for a in answers])
    print(f"\n📝 Распределение по частям:")
    for part, count in sorted(parts.items()):
        print(f"  Part {part}: {count} ответов")
    
    # Разделяем ответы по частям для дальнейшего анализа
    part1_answers = [a for a in answers if a['part'] == '1']
    part2_answers = [a for a in answers if a['part'] == '2']
    part3_answers = [a for a in answers if a['part'] == '3']
    
    # 3. Распределение по уровням (overall) - общее и по частям
    overalls = [float(a['target_band_overall']) for a in answers]
    part1_overalls = [float(a['target_band_overall']) for a in part1_answers]
    part2_overalls = [float(a['target_band_overall']) for a in part2_answers] if part2_answers else []
    part3_overalls = [float(a['target_band_overall']) for a in part3_answers] if part3_answers else []
    
    print(f"\n🎯 Распределение по уровням (overall):")
    print(f"  Общее:")
    print(f"    Минимум: {min(overalls):.1f}")
    print(f"    Максимум: {max(overalls):.1f}")
    print(f"    Среднее: {np.mean(overalls):.2f}")
    print(f"    Медиана: {np.median(overalls):.2f}")
    print(f"    Стандартное отклонение: {np.std(overalls):.2f}")
    
    if part1_overalls:
        print(f"  Part 1 ({len(part1_overalls)} ответов):")
        print(f"    Среднее: {np.mean(part1_overalls):.2f}, Медиана: {np.median(part1_overalls):.2f}")
    if part2_overalls:
        print(f"  Part 2 ({len(part2_overalls)} ответов):")
        print(f"    Среднее: {np.mean(part2_overalls):.2f}, Медиана: {np.median(part2_overalls):.2f}")
    if part3_overalls:
        print(f"  Part 3 ({len(part3_overalls)} ответов):")
        print(f"    Среднее: {np.mean(part3_overalls):.2f}, Медиана: {np.median(part3_overalls):.2f}")
    
    # Гистограмма по уровням
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.hist(overalls, bins=20, edgecolor='black', alpha=0.7)
    plt.xlabel('Band Score (Overall)')
    plt.ylabel('Количество ответов')
    plt.title('Распределение по уровням (Overall)')
    plt.grid(True, alpha=0.3)
    
    # 4. Распределение длины ответов - общее и по частям
    durations = [int(a['duration_sec']) for a in answers if a['duration_sec']]
    part1_durations = [int(a['duration_sec']) for a in part1_answers if a.get('duration_sec')]
    part2_durations = [int(a['duration_sec']) for a in part2_answers if a.get('duration_sec')] if part2_answers else []
    part3_durations = [int(a['duration_sec']) for a in part3_answers if a.get('duration_sec')] if part3_answers else []
    
    print(f"\n⏱️  Распределение длины ответов (секунды):")
    print(f"  Общее:")
    print(f"    Минимум: {min(durations)}")
    print(f"    Максимум: {max(durations)}")
    print(f"    Среднее: {np.mean(durations):.1f}")
    print(f"    Медиана: {np.median(durations):.1f}")
    
    if part1_durations:
        print(f"  Part 1: среднее={np.mean(part1_durations):.1f}, медиана={np.median(part1_durations):.1f}")
    if part2_durations:
        print(f"  Part 2: среднее={np.mean(part2_durations):.1f}, медиана={np.median(part2_durations):.1f}")
    if part3_durations:
        print(f"  Part 3: среднее={np.mean(part3_durations):.1f}, медиана={np.median(part3_durations):.1f}")
    
    plt.subplot(1, 2, 2)
    plt.hist(durations, bins=30, edgecolor='black', alpha=0.7, color='orange')
    plt.xlabel('Длительность (секунды)')
    plt.ylabel('Количество ответов')
    plt.title('Распределение длительности ответов')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('eda_overall_duration.png', dpi=150, bbox_inches='tight')
    print(f"\n✅ Сохранена гистограмма: eda_overall_duration.png")
    
    # 5. Разброс субскоров
    fcs = [float(a['target_band_fc']) for a in answers]
    lrs = [float(a['target_band_lr']) for a in answers]
    gras = [float(a['target_band_gra']) for a in answers]
    prs = [float(a['target_band_pr']) for a in answers]
    
    print(f"\n📈 Статистика субскоров:")
    print(f"  FC:  среднее={np.mean(fcs):.2f},  std={np.std(fcs):.2f}")
    print(f"  LR:  среднее={np.mean(lrs):.2f},  std={np.std(lrs):.2f}")
    print(f"  GRA: среднее={np.mean(gras):.2f}, std={np.std(gras):.2f}")
    print(f"  PR:  среднее={np.mean(prs):.2f},  std={np.std(prs):.2f}")
    
    # Визуализация разброса субскоров
    plt.figure(figsize=(14, 5))
    
    plt.subplot(1, 2, 1)
    plt.hist(fcs, bins=15, alpha=0.5, label='FC', edgecolor='black')
    plt.hist(lrs, bins=15, alpha=0.5, label='LR', edgecolor='black')
    plt.hist(gras, bins=15, alpha=0.5, label='GRA', edgecolor='black')
    plt.hist(prs, bins=15, alpha=0.5, label='PR', edgecolor='black')
    plt.xlabel('Band Score')
    plt.ylabel('Количество')
    plt.title('Распределение субскоров')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Разброс относительно overall
    plt.subplot(1, 2, 2)
    fc_diff = [fcs[i] - overalls[i] for i in range(len(fcs))]
    lr_diff = [lrs[i] - overalls[i] for i in range(len(lrs))]
    gra_diff = [gras[i] - overalls[i] for i in range(len(gras))]
    pr_diff = [prs[i] - overalls[i] for i in range(len(prs))]
    
    plt.hist(fc_diff, bins=15, alpha=0.5, label='FC', edgecolor='black')
    plt.hist(lr_diff, bins=15, alpha=0.5, label='LR', edgecolor='black')
    plt.hist(gra_diff, bins=15, alpha=0.5, label='GRA', edgecolor='black')
    plt.hist(pr_diff, bins=15, alpha=0.5, label='PR', edgecolor='black')
    plt.xlabel('Разница от Overall')
    plt.ylabel('Количество')
    plt.title('Разброс субскоров относительно Overall')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axvline(x=0, color='red', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('eda_subbands.png', dpi=150, bbox_inches='tight')
    print(f"✅ Сохранена гистограмма: eda_subbands.png")
    
    # 6. Распределение по уровням пользователей
    user_levels = []
    user_answer_counts = defaultdict(int)
    user_answer_levels = defaultdict(list)
    
    for answer in answers:
        user_id = answer['user_id']
        user_level = users.get(user_id)
        if user_level:
            user_levels.append(user_level)
            user_answer_counts[user_id] += 1
            user_answer_levels[user_id].append(float(answer['target_band_overall']))
    
    print(f"\n👥 Распределение по уровням пользователей:")
    print(f"  Минимум: {min(user_levels):.1f}")
    print(f"  Максимум: {max(user_levels):.1f}")
    print(f"  Среднее: {np.mean(user_levels):.2f}")
    
    # Визуализация: уровень пользователя vs уровень ответов
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.hist(user_levels, bins=15, edgecolor='black', alpha=0.7, color='green')
    plt.xlabel('Level Estimate пользователя')
    plt.ylabel('Количество пользователей')
    plt.title('Распределение уровней пользователей')
    plt.grid(True, alpha=0.3)
    
    # Разброс ответов пользователя относительно его уровня
    plt.subplot(1, 2, 2)
    variations = []
    for user_id, user_level in users.items():
        if user_id in user_answer_levels:
            for answer_level in user_answer_levels[user_id]:
                variations.append(answer_level - user_level)
    
    plt.hist(variations, bins=20, edgecolor='black', alpha=0.7, color='purple')
    plt.xlabel('Разница: Ответ - Level Estimate')
    plt.ylabel('Количество ответов')
    plt.title('Вариация ответов относительно уровня пользователя')
    plt.grid(True, alpha=0.3)
    plt.axvline(x=0, color='red', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('eda_users.png', dpi=150, bbox_inches='tight')
    print(f"✅ Сохранена гистограмма: eda_users.png")
    
    # 7. Статистика по quality_flag
    if 'quality_flag' in answers[0]:
        quality_flags = Counter([a['quality_flag'] for a in answers])
        print(f"\n🏷️  Распределение по quality_flag:")
        for flag, count in quality_flags.items():
            print(f"  {flag}: {count} ответов")
        
        # Визуализация quality_flag
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        flags = list(quality_flags.keys())
        counts = list(quality_flags.values())
        plt.bar(flags, counts, edgecolor='black', alpha=0.7, color=['green' if f == 'ok' else 'red' for f in flags])
        plt.xlabel('Quality Flag')
        plt.ylabel('Количество ответов')
        plt.title('Распределение по Quality Flag')
        plt.grid(True, alpha=0.3, axis='y')
        
        # Распределение overall внутри quality_flag
        plt.subplot(1, 2, 2)
        ok_overalls = [float(a['target_band_overall']) for a in answers if a.get('quality_flag') == 'ok']
        garbage_overalls = [float(a['target_band_overall']) for a in answers if a.get('quality_flag') == 'garbage']
        
        if ok_overalls and garbage_overalls:
            plt.hist(ok_overalls, bins=15, alpha=0.6, label='ok', edgecolor='black', color='green')
            plt.hist(garbage_overalls, bins=15, alpha=0.6, label='garbage', edgecolor='black', color='red')
            plt.xlabel('Band Score (Overall)')
            plt.ylabel('Количество')
            plt.title('Распределение Overall по Quality Flag')
            plt.legend()
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('eda_quality_flag.png', dpi=150, bbox_inches='tight')
        print(f"✅ Сохранена гистограмма: eda_quality_flag.png")
    
    # 8. Корреляция между субскорами
    print(f"\n🔗 Корреляция между субскорами:")
    correlations = {
        'FC-LR': np.corrcoef(fcs, lrs)[0, 1],
        'FC-GRA': np.corrcoef(fcs, gras)[0, 1],
        'FC-PR': np.corrcoef(fcs, prs)[0, 1],
        'LR-GRA': np.corrcoef(lrs, gras)[0, 1],
        'LR-PR': np.corrcoef(lrs, prs)[0, 1],
        'GRA-PR': np.corrcoef(gras, prs)[0, 1],
    }
    for pair, corr in correlations.items():
        print(f"  {pair}: {corr:.3f}")
    
    print("\n" + "=" * 60)
    print("✅ EDA завершен!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        analyze_dataset()
    except ImportError:
        print("❌ Ошибка: требуется установить matplotlib и numpy")
        print("   pip install matplotlib numpy")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

