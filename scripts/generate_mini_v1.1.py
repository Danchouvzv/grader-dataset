#!/usr/bin/env python3
"""
Скрипт генерации Mini-v1.1 (Pilot)
Цель: Создать небольшую выборку (150-200 ответов) с новыми генераторами для проверки метрик baseline.
"""

import csv
import random
import json
from datetime import datetime
from improved_generation_v2 import generate_part1_answer_v2, generate_part2_answer_v2
from generate_synthetic_expansion import generate_realistic_subbands, load_existing_data, get_next_ids, generate_new_users, generate_new_sessions, generate_part1_questions
from generate_part2_expansion import generate_part2_questions
from improve_generation import determine_quality_flag

CONFIG_FILE = 'config_v1.1_generation.json'

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def main():
    print("=" * 70)
    print("ГЕНЕРАЦИЯ MINI-V1.1 (PILOT)")
    print("=" * 70)
    
    config = load_config()
    random.seed(config['random_seed'])
    print(f"🔧 Config loaded. Seed: {config['random_seed']}")
    
    # Загрузка данных
    print("\n📂 Загрузка существующих данных...")
    users, sessions, answers = load_existing_data()
    next_answer_id, next_session_id = get_next_ids(answers)
    print(f"   Next Answer ID: ans_{next_answer_id:03d}")
    
    # Получаем пользователей и сессии
    all_user_ids = list(users.keys())
    all_session_ids = [s['session_id'] for s in sessions]
    
    # Генерация
    new_answers = []
    answer_id_counter = next_answer_id
    
    # Распределение для mini-batch (по ~50-60 на диапазон)
    # Low: 3.5-4.5
    # Medium: 5.0-6.0
    # High: 6.5-8.0
    targets = {
        'low': {'range': [3.5, 4.0, 4.5], 'count': 50},
        'medium': {'range': [5.0, 5.5, 6.0], 'count': 60},
        'high': {'range': [6.5, 7.0, 7.5, 8.0], 'count': 50}
    }
    
    p1_questions = generate_part1_questions()
    p2_questions = generate_part2_questions()
    
    print("\n🚀 Начало генерации...")
    
    for group, params in targets.items():
        print(f"   Группа {group}: {params['count']} ответов...")
        bands = params['range']
        count_per_band = params['count'] // len(bands)
        
        for overall in bands:
            for _ in range(count_per_band):
                # Randomly choose Part 1 or Part 2
                part = random.choice([1, 2])
                
                # Subscores
                fc, lr, gra, pr = generate_realistic_subbands(overall)
                
                # User/Session
                user_id = random.choice(all_user_ids)
                session_id = random.choice(all_session_ids)
                
                if part == 1:
                    q_id, q_text = random.choice(p1_questions)
                    answer_text, duration = generate_part1_answer_v2(q_text, overall, fc, lr, gra, pr)
                else:
                    q_id, q_text = random.choice(p2_questions)
                    answer_text, duration = generate_part2_answer_v2(q_text, overall, fc, lr, gra, pr)
                
                quality_flag = determine_quality_flag(overall)
                
                new_answer = {
                    'answer_id': f'ans_{answer_id_counter:03d}',
                    'session_id': session_id,
                    'user_id': user_id,
                    'part': str(part),
                    'question_id': q_id,
                    'question_text': q_text,
                    'answer_text': answer_text,
                    'duration_sec': str(duration),
                    'target_band_overall': str(overall),
                    'target_band_fc': str(fc),
                    'target_band_lr': str(lr),
                    'target_band_gra': str(gra),
                    'target_band_pr': str(pr),
                    'transcript_raw': answer_text,
                    'source_type': 'synthetic_mini_v1.1',
                    'quality_flag': quality_flag
                }
                
                new_answers.append(new_answer)
                answer_id_counter += 1

    # Сохранение
    filename = 'answers_mini_v1.1.csv'
    print(f"\n💾 Сохранение {len(new_answers)} ответов в {filename}...")
    
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['answer_id', 'session_id', 'user_id', 'part', 'question_id', 'question_text',
                     'answer_text', 'duration_sec', 'target_band_overall', 'target_band_fc',
                     'target_band_lr', 'target_band_gra', 'target_band_pr', 'transcript_raw',
                     'source_type', 'quality_flag']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_answers)
        
    print(f"✅ Готово! Файл: {filename}")

if __name__ == "__main__":
    main()

