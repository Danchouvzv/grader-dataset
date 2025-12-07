#!/usr/bin/env python3
"""
Создание train/val/test split с учетом session_id и стратификации
- Не допускает утечку по session_id
- Стратификация по Part и Band-группам
"""

import csv
import random
from collections import defaultdict

def get_band_group(overall: float) -> str:
    """Определяет группу бэнда"""
    if overall <= 5.5:
        return 'low'
    elif overall <= 6.5:
        return 'mid'
    else:
        return 'high'

def create_split(answers_file: str, train_ratio: float = 0.8, val_ratio: float = 0.1):
    """Создает train/val/test split"""
    
    # Загружаем ответы
    answers = []
    with open(answers_file, 'r', encoding='utf-8') as f:
        answers = list(csv.DictReader(f))
    
    print(f"📂 Загружено: {len(answers)} ответов")
    
    # Группируем по session_id
    by_session = defaultdict(list)
    for answer in answers:
        session_id = answer.get('session_id', '')
        by_session[session_id].append(answer)
    
    print(f"📋 Уникальных сессий: {len(by_session)}")
    
    # Стратифицируем сессии по Part и Band
    sessions_by_strata = defaultdict(list)
    
    for session_id, session_answers in by_session.items():
        # Определяем доминирующий Part
        parts = [a.get('part', '') for a in session_answers]
        part_counts = defaultdict(int)
        for p in parts:
            part_counts[p] += 1
        dominant_part = max(part_counts.items(), key=lambda x: x[1])[0]
        
        # Определяем доминирующий Band
        overalls = []
        for a in session_answers:
            try:
                overalls.append(float(a.get('target_band_overall', 0)))
            except:
                pass
        
        if overalls:
            avg_overall = sum(overalls) / len(overalls)
            band_group = get_band_group(avg_overall)
        else:
            band_group = 'mid'
        
        strata = f"{dominant_part}_{band_group}"
        sessions_by_strata[strata].append(session_id)
    
    print(f"\n📊 Стратификация:")
    for strata, sessions in sessions_by_strata.items():
        print(f"   {strata}: {len(sessions)} сессий")
    
    # Разделяем сессии на train/val/test
    random.seed(42)
    
    train_sessions = set()
    val_sessions = set()
    test_sessions = set()
    
    for strata, sessions in sessions_by_strata.items():
        random.shuffle(sessions)
        
        n = len(sessions)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        
        train_sessions.update(sessions[:n_train])
        val_sessions.update(sessions[n_train:n_train+n_val])
        test_sessions.update(sessions[n_train+n_val:])
    
    print(f"\n📊 Разделение сессий:")
    print(f"   Train: {len(train_sessions)} сессий")
    print(f"   Val: {len(val_sessions)} сессий")
    print(f"   Test: {len(test_sessions)} сессий")
    
    # Разделяем ответы
    train_answers = []
    val_answers = []
    test_answers = []
    
    for answer in answers:
        session_id = answer.get('session_id', '')
        if session_id in train_sessions:
            train_answers.append(answer)
        elif session_id in val_sessions:
            val_answers.append(answer)
        elif session_id in test_sessions:
            test_answers.append(answer)
        else:
            # Если сессия не попала никуда (не должно быть), идем в train
            train_answers.append(answer)
    
    print(f"\n📊 Разделение ответов:")
    print(f"   Train: {len(train_answers)} ответов ({len(train_answers)/len(answers)*100:.1f}%)")
    print(f"   Val: {len(val_answers)} ответов ({len(val_answers)/len(answers)*100:.1f}%)")
    print(f"   Test: {len(test_answers)} ответов ({len(test_answers)/len(answers)*100:.1f}%)")
    
    # Проверяем стратификацию
    print(f"\n📊 Стратификация по частям (Train):")
    train_parts = defaultdict(int)
    for a in train_answers:
        train_parts[a.get('part', '')] += 1
    for part in sorted(train_parts.keys()):
        print(f"   Part {part}: {train_parts[part]} ({train_parts[part]/len(train_answers)*100:.1f}%)")
    
    print(f"\n📊 Стратификация по бэндам (Train):")
    train_bands = defaultdict(int)
    for a in train_answers:
        try:
            overall = float(a.get('target_band_overall', 0))
            band_group = get_band_group(overall)
            train_bands[band_group] += 1
        except:
            pass
    for band in ['low', 'mid', 'high']:
        count = train_bands.get(band, 0)
        print(f"   {band}: {count} ({count/len(train_answers)*100:.1f}%)")
    
    # Сохраняем
    fieldnames = ['answer_id', 'session_id', 'user_id', 'part', 'question_id', 'question_text',
                 'answer_text', 'duration_sec', 'target_band_overall', 'target_band_fc',
                 'target_band_lr', 'target_band_gra', 'target_band_pr', 'transcript_raw',
                 'source_type', 'quality_flag', 'sample_weight', 'is_inconsistent']
    
    for split_name, split_answers in [('train', train_answers), ('val', val_answers), ('test', test_answers)]:
        output_file = f'dataset_versions/v1.3/{split_name}.csv'
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for answer in split_answers:
                row = {k: answer.get(k, '') for k in fieldnames}
                writer.writerow(row)
        print(f"\n💾 {split_name.capitalize()} сохранен в {output_file}")
    
    # Сохраняем метаданные
    metadata = {
        'total_answers': len(answers),
        'train_count': len(train_answers),
        'val_count': len(val_answers),
        'test_count': len(test_answers),
        'train_ratio': len(train_answers) / len(answers),
        'val_ratio': len(val_answers) / len(answers),
        'test_ratio': len(test_answers) / len(answers),
        'total_sessions': len(by_session),
        'train_sessions': len(train_sessions),
        'val_sessions': len(val_sessions),
        'test_sessions': len(test_sessions),
    }
    
    import json
    with open('dataset_versions/v1.3/split_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n💾 Метаданные сохранены в dataset_versions/v1.3/split_metadata.json")
    print(f"\n✅ Split создан успешно")

if __name__ == '__main__':
    import sys
    answers_file = sys.argv[1] if len(sys.argv) > 1 else 'dataset_versions/v1.3/answers_fixed.csv'
    create_split(answers_file)

