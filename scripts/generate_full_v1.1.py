#!/usr/bin/env python3
"""
Скрипт генерации полной версии v1.1
Объединяет все генераторы, использует конфиг и логирует процесс.
"""

import csv
import random
import json
import os
import shutil
from datetime import datetime
from generate_synthetic_expansion import generate_realistic_subbands, load_existing_data, get_next_ids, generate_part1_questions, generate_part1_answer
from generate_part2_expansion import generate_part2_questions, generate_part2_answer
from generate_part3_expansion import generate_part3_questions, generate_part3_answer
from improved_generation_v2 import generate_part1_answer_v2, generate_part2_answer_v2
from improve_generation import determine_quality_flag

CONFIG_FILE = 'configs/config_v1.1_generation.json'
LOG_DIR = 'logs'
OUTPUT_DIR = 'dataset_versions/v1.1'

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def log_message(message: str, log_file: str):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    with open(log_file, 'a') as f:
        f.write(formatted_message + '\n')

def main():
    start_time = datetime.now()
    log_file = os.path.join(LOG_DIR, f"generation_v1.1_{start_time.strftime('%Y%m%d_%H%M')}.txt")
    
    # Создаем директории
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    log_message("=" * 70, log_file)
    log_message("ЗАПУСК ПОЛНОЙ ГЕНЕРАЦИИ V1.1", log_file)
    log_message("=" * 70, log_file)
    
    # Загрузка конфига
    config = load_config()
    random.seed(config['random_seed'])
    log_message(f"🔧 Config loaded from {CONFIG_FILE}", log_file)
    log_message(f"🔧 Random seed: {config['random_seed']}", log_file)
    
    # Копирование v1.0 как базы
    log_message("\n📂 Копирование v1.0 как базы...", log_file)
    v1_0_dir = 'dataset_versions/v1.0'
    for file in ['users.csv', 'sessions.csv', 'answers.csv']:
        src = os.path.join(v1_0_dir, file)
        dst = os.path.join(OUTPUT_DIR, file)
        shutil.copy2(src, dst)
        log_message(f"   Copied {src} -> {dst}", log_file)
    
    # Загрузка данных из НОВОЙ директории (чтобы дописывать туда)
    # Используем функции загрузки, но указываем путь к v1.1 файлам вручную или через os.chdir
    # Проще просто загрузить данные в память и писать в файлы v1.1
    
    users_v1_1_path = os.path.join(OUTPUT_DIR, 'users.csv')
    sessions_v1_1_path = os.path.join(OUTPUT_DIR, 'sessions.csv')
    answers_v1_1_path = os.path.join(OUTPUT_DIR, 'answers.csv')
    
    # Читаем текущие данные
    with open(users_v1_1_path, 'r', encoding='utf-8') as f:
        users = list(csv.DictReader(f))
    with open(sessions_v1_1_path, 'r', encoding='utf-8') as f:
        sessions = list(csv.DictReader(f))
    with open(answers_v1_1_path, 'r', encoding='utf-8') as f:
        answers = list(csv.DictReader(f))
        
    log_message(f"   Base v1.0 stats: {len(users)} users, {len(sessions)} sessions, {len(answers)} answers", log_file)
    
    # Определяем ID
    next_answer_id = 0
    for a in answers:
        try:
            aid = int(a['answer_id'].split('_')[1])
            next_answer_id = max(next_answer_id, aid)
        except: pass
    next_answer_id += 1
    log_message(f"   Next Answer ID: ans_{next_answer_id:03d}", log_file)
    
    all_user_ids = [u['user_id'] for u in users]
    all_session_ids = [s['session_id'] for s in sessions]
    
    # Цели генерации
    targets = config['targets']
    log_message(f"\n🎯 Targets: Part 1: +{targets['part1_count']}, Part 2: +{targets['part2_count']}, Part 3: +{targets['part3_count']}", log_file)
    
    # Подготовка вопросов
    p1_questions = generate_part1_questions()
    p2_questions = generate_part2_questions()
    p3_questions = generate_part3_questions()
    
    new_answers = []
    answer_id_counter = next_answer_id
    
    # Генерация Part 1
    log_message("\n🚀 Генерация Part 1...", log_file)
    count_p1 = 0
    while count_p1 < targets['part1_count']:
        # Распределение band (упрощенное для скорости, но можно взять из конфига)
        # В конфиге "band_distribution": {"low": 0.2, "medium": 0.5, "high": 0.3}
        r = random.random()
        if r < 0.2: overall = random.choice([3.0, 3.5, 4.0, 4.5])
        elif r < 0.7: overall = random.choice([5.0, 5.5, 6.0, 6.5])
        else: overall = random.choice([7.0, 7.5, 8.0, 8.5])
        
        q_id, q_text = random.choice(p1_questions)
        fc, lr, gra, pr = generate_realistic_subbands(overall)
        answer_text, duration = generate_part1_answer_v2(q_text, overall, fc, lr, gra, pr)
        
        new_answers.append(create_answer_dict(answer_id_counter, random.choice(all_session_ids), random.choice(all_user_ids),
                                            '1', q_id, q_text, answer_text, duration, overall, fc, lr, gra, pr))
        answer_id_counter += 1
        count_p1 += 1
        
    log_message(f"   Generated {count_p1} Part 1 answers", log_file)

    # Генерация Part 2
    log_message("🚀 Генерация Part 2...", log_file)
    count_p2 = 0
    while count_p2 < targets['part2_count']:
        r = random.random()
        if r < 0.2: overall = random.choice([3.5, 4.0, 4.5])
        elif r < 0.7: overall = random.choice([5.0, 5.5, 6.0, 6.5])
        else: overall = random.choice([7.0, 7.5, 8.0, 8.5])
        
        q_id, q_text = random.choice(p2_questions)
        fc, lr, gra, pr = generate_realistic_subbands(overall)
        answer_text, duration = generate_part2_answer_v2(q_text, overall, fc, lr, gra, pr)
        
        new_answers.append(create_answer_dict(answer_id_counter, random.choice(all_session_ids), random.choice(all_user_ids),
                                            '2', q_id, q_text, answer_text, duration, overall, fc, lr, gra, pr))
        answer_id_counter += 1
        count_p2 += 1
        
    log_message(f"   Generated {count_p2} Part 2 answers", log_file)
    
    # Генерация Part 3
    log_message("🚀 Генерация Part 3...", log_file)
    count_p3 = 0
    while count_p3 < targets['part3_count']:
        r = random.random()
        if r < 0.2: overall = random.choice([3.5, 4.0, 4.5])
        elif r < 0.7: overall = random.choice([5.0, 5.5, 6.0, 6.5])
        else: overall = random.choice([7.0, 7.5, 8.0, 8.5])
        
        q_id, q_text = random.choice(p3_questions)
        fc, lr, gra, pr = generate_realistic_subbands(overall)
        # Используем обновленную функцию из generate_part3_expansion (которая уже v2)
        answer_text, duration = generate_part3_answer(q_text, overall, fc, lr, gra, pr)
        
        new_answers.append(create_answer_dict(answer_id_counter, random.choice(all_session_ids), random.choice(all_user_ids),
                                            '3', q_id, q_text, answer_text, duration, overall, fc, lr, gra, pr))
        answer_id_counter += 1
        count_p3 += 1
        
    log_message(f"   Generated {count_p3} Part 3 answers", log_file)
    
    # Сохранение
    log_message(f"\n💾 Добавление {len(new_answers)} новых ответов в {answers_v1_1_path}...", log_file)
    
    with open(answers_v1_1_path, 'a', encoding='utf-8', newline='') as f:
        fieldnames = ['answer_id', 'session_id', 'user_id', 'part', 'question_id', 'question_text',
                     'answer_text', 'duration_sec', 'target_band_overall', 'target_band_fc',
                     'target_band_lr', 'target_band_gra', 'target_band_pr', 'transcript_raw',
                     'source_type', 'quality_flag']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(new_answers)
        
    log_message("\n✅ ГЕНЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО", log_file)
    log_message(f"   Total answers in v1.1: {len(answers) + len(new_answers)}", log_file)

def create_answer_dict(aid, sid, uid, part, qid, qtext, text, dur, overall, fc, lr, gra, pr):
    return {
        'answer_id': f'ans_{aid:03d}',
        'session_id': sid,
        'user_id': uid,
        'part': part,
        'question_id': qid,
        'question_text': qtext,
        'answer_text': text,
        'duration_sec': str(dur),
        'target_band_overall': str(overall),
        'target_band_fc': str(fc),
        'target_band_lr': str(lr),
        'target_band_gra': str(gra),
        'target_band_pr': str(pr),
        'transcript_raw': text,
        'source_type': 'synthetic_v1.1',
        'quality_flag': determine_quality_flag(overall)
    }

if __name__ == "__main__":
    main()

