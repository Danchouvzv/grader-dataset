#!/usr/bin/env python3
"""
Генерация preview версии v1.1 с улучшенной генерацией и error injection

Создает небольшой preview (300-400 ответов) для тестирования улучшений
"""

import csv
import random
from datetime import datetime, timedelta
from improved_generation_v2 import generate_part1_answer_v2, generate_part2_answer_v2, extract_topic_improved
from generate_synthetic_expansion import generate_realistic_subbands, round_to_half
from improve_generation import determine_quality_flag

def load_existing_data():
    """Загружает существующие данные"""
    users = {}
    sessions = []
    
    with open('users.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            users[row['user_id']] = float(row['level_estimate']) if row['level_estimate'] else None
    
    with open('sessions.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        sessions = list(reader)
    
    return users, sessions

def get_next_answer_id():
    """Получает следующий answer_id"""
    max_id = 0
    try:
        with open('answers.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    ans_num = int(row['answer_id'].split('_')[1])
                    max_id = max(max_id, ans_num)
                except:
                    pass
    except:
        pass
    return max_id + 1

def generate_part1_questions_sample() -> list:
    """Выборка вопросов Part 1 для preview"""
    return [
        ("q_part1_122", "Do you like listening to music?"),
        ("q_part1_123", "How often do you use social media?"),
        ("q_part1_124", "What's your favorite season?"),
        ("q_part1_125", "How do you relax after work?"),
        ("q_part1_126", "Do you prefer tea or coffee?"),
        ("q_part1_127", "What kind of food do you prefer?"),
        ("q_part1_128", "Do you enjoy reading?"),
        ("q_part1_129", "How do you stay healthy?"),
        ("q_part1_130", "Do you prefer mornings or evenings?"),
    ]

def generate_part2_questions_sample() -> list:
    """Выборка вопросов Part 2 для preview"""
    return [
        ("q_part2_100", "Describe a place you visited."),
        ("q_part2_101", "Describe a person who influenced you."),
        ("q_part2_102", "Describe a memorable event."),
        ("q_part2_103", "Describe a skill you learned."),
        ("q_part2_104", "Describe a gift you received."),
    ]

def main():
    print("=" * 70)
    print("ГЕНЕРАЦИЯ PREVIEW V1.1")
    print("=" * 70)
    
    # Загружаем данные
    print("\n📂 Загрузка данных...")
    users, sessions = load_existing_data()
    print(f"   Пользователей: {len(users)}")
    print(f"   Сессий: {len(sessions)}")
    
    # Получаем следующий ID
    next_answer_id = get_next_answer_id()
    print(f"   Следующий answer_id: ans_{next_answer_id:03d}")
    
    # Генерируем вопросы
    part1_questions = generate_part1_questions_sample()
    part2_questions = generate_part2_questions_sample()
    
    print(f"\n📝 Part 1 вопросов: {len(part1_questions)}")
    print(f"📝 Part 2 вопросов: {len(part2_questions)}")
    
    # Получаем всех пользователей и сессии
    all_user_ids = list(users.keys())
    all_session_ids = [s['session_id'] for s in sessions]
    
    # Генерируем ответы
    target_count = 350  # Preview размер
    print(f"\n📝 Генерируем {target_count} ответов для preview v1.1...")
    
    new_answers = []
    
    # Распределение: 60% Part 1, 40% Part 2
    part1_count = int(target_count * 0.6)
    part2_count = target_count - part1_count
    
    # Band distribution
    band_distribution = {
        4.0: 20, 4.5: 15, 5.0: 25, 5.5: 30,
        6.0: 80, 6.5: 40, 7.0: 60, 7.5: 50, 8.0: 20, 8.5: 10
    }
    
    answer_id_counter = next_answer_id
    question_idx_p1 = 0
    question_idx_p2 = 0
    
    # Part 1
    for overall, count in band_distribution.items():
        for _ in range(min(count, part1_count // len(band_distribution))):
            if question_idx_p1 >= len(part1_questions):
                question_idx_p1 = 0
            
            q_id, q_text = part1_questions[question_idx_p1]
            question_idx_p1 += 1
            
            # Генерируем субскоры
            fc, lr, gra, pr = generate_realistic_subbands(overall)
            
            # Генерируем ответ с улучшенной генерацией
            answer_text, duration = generate_part1_answer_v2(q_text, overall, fc, lr, gra, pr)
            
            # Выбираем пользователя и сессию
            user_id = random.choice(all_user_ids)
            session_id = random.choice(all_session_ids)
            
            quality = determine_quality_flag(overall)
            
            new_answer = {
                'answer_id': f'ans_{answer_id_counter:03d}',
                'session_id': session_id,
                'user_id': user_id,
                'part': '1',
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
                'source_type': 'synthetic_v1.1',
                'quality_flag': quality
            }
            
            new_answers.append(new_answer)
            answer_id_counter += 1
    
    # Part 2
    for overall, count in band_distribution.items():
        for _ in range(min(count, part2_count // len(band_distribution))):
            if question_idx_p2 >= len(part2_questions):
                question_idx_p2 = 0
            
            q_id, q_text = part2_questions[question_idx_p2]
            question_idx_p2 += 1
            
            # Генерируем субскоры
            fc, lr, gra, pr = generate_realistic_subbands(overall)
            
            # Генерируем ответ с улучшенной генерацией
            answer_text, duration = generate_part2_answer_v2(q_text, overall, fc, lr, gra, pr)
            
            # Выбираем пользователя и сессию
            user_id = random.choice(all_user_ids)
            session_id = random.choice(all_session_ids)
            
            quality = determine_quality_flag(overall)
            
            new_answer = {
                'answer_id': f'ans_{answer_id_counter:03d}',
                'session_id': session_id,
                'user_id': user_id,
                'part': '2',
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
                'source_type': 'synthetic_v1.1',
                'quality_flag': quality
            }
            
            new_answers.append(new_answer)
            answer_id_counter += 1
    
    # Сохраняем в отдельный файл для preview
    preview_file = 'answers_v1.1_preview.csv'
    print(f"\n💾 Сохранение preview в {preview_file}...")
    
    with open(preview_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['answer_id', 'session_id', 'user_id', 'part', 'question_id', 'question_text',
                     'answer_text', 'duration_sec', 'target_band_overall', 'target_band_fc',
                     'target_band_lr', 'target_band_gra', 'target_band_pr', 'transcript_raw',
                     'source_type', 'quality_flag']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_answers)
    
    # Статистика
    print("\n" + "=" * 70)
    print("✅ СТАТИСТИКА PREVIEW V1.1")
    print("=" * 70)
    print(f"   ✅ Создано ответов: {len(new_answers)}")
    
    part_counts = {}
    for a in new_answers:
        part = a['part']
        part_counts[part] = part_counts.get(part, 0) + 1
    
    for part in sorted(part_counts.keys()):
        print(f"   Part {part}: {part_counts[part]} ответов")
    
    # Проверка разнообразия субскоров
    varied_3plus = sum(1 for a in new_answers if len(set([
        float(a['target_band_fc']), float(a['target_band_lr']),
        float(a['target_band_gra']), float(a['target_band_pr'])
    ])) >= 3)
    
    print(f"   ✅ Ответов с 3+ уникальными субскорами: {varied_3plus}/{len(new_answers)} ({varied_3plus/len(new_answers)*100:.1f}%)")
    
    print(f"\n✅ Preview v1.1 создан в {preview_file}")
    print("   Используйте этот файл для тестирования улучшений перед полным обновлением датасета")

if __name__ == '__main__':
    main()

