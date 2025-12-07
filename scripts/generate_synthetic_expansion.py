#!/usr/bin/env python3
"""
Synthetic Expansion Script для расширения датасета IELTS Speaking

Этап 1.1: Генерация новых ответов с сохранением разнообразия субскоров
Цель: +500-750 Part 1, +400-600 Part 2, +300-450 Part 3
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from improved_generation_v2 import generate_part1_answer_v2
from improve_generation import determine_quality_flag

def round_to_half(value: float) -> float:
    """Округляет до ближайшего 0.5"""
    return round(value * 2) / 2

def generate_realistic_subbands(overall: float) -> Tuple[float, float, float, float]:
    """
    Генерирует реалистичные субскоры с разнообразием вокруг overall
    """
    # Разнообразные комбинации субскоров
    variations = [
        (0.5, 0.0, -0.5, 0.0),  # FC высокий, GRA низкий
        (-0.5, 0.5, 0.0, 0.0),  # FC низкий, LR высокий
        (0.0, 0.0, -0.5, 0.5),  # GRA низкий, PR высокий
        (0.5, -0.5, 0.5, -0.5), # FC/GRA высокие, LR/PR низкие
        (-0.5, 0.5, 0.5, -0.5), # FC низкий, LR/GRA высокие
        (0.0, 0.5, -0.5, 0.0),  # LR высокий, GRA низкий
        (0.5, 0.0, 0.0, -0.5),  # FC высокий, PR низкий
        (-0.5, 0.0, 0.5, 0.0),  # FC низкий, GRA высокий
        (0.0, -0.5, 0.0, 0.5),  # LR низкий, PR высокий
        (0.5, 0.5, -0.5, -0.5), # FC/LR высокие, GRA/PR низкие
        (-0.5, -0.5, 0.5, 0.5), # FC/LR низкие, GRA/PR высокие
        (1.0, 0.0, -0.5, 0.0),  # FC очень высокий, GRA низкий
        (-0.5, 1.0, 0.0, 0.0),  # FC низкий, LR очень высокий
        (0.0, 0.0, 1.0, -0.5),  # GRA очень высокий, PR низкий
        (0.0, 0.0, -0.5, 1.0),  # GRA низкий, PR очень высокий
    ]
    
    # Для низких уровней чаще проседают GRA и PR
    if overall <= 4.5:
        variations.extend([
            (0.0, 0.0, -1.0, -0.5),
            (0.0, -0.5, -1.0, 0.0),
            (-0.5, 0.0, -1.0, 0.0),
        ])
    
    # Для высоких уровней LR и FC часто выше
    if overall >= 7.0:
        variations.extend([
            (0.5, 1.0, 0.0, 0.0),
            (1.0, 0.5, 0.0, 0.0),
            (0.5, 0.5, 0.5, 0.0),
        ])
    
    fc_var, lr_var, gra_var, pr_var = random.choice(variations)
    
    fc = round_to_half(max(3.0, min(9.0, overall + fc_var)))
    lr = round_to_half(max(3.0, min(9.0, overall + lr_var)))
    gra = round_to_half(max(3.0, min(9.0, overall + gra_var)))
    pr = round_to_half(max(3.0, min(9.0, overall + pr_var)))
    
    return fc, lr, gra, pr

def load_existing_data():
    """Загружает существующие данные"""
    users = {}
    sessions = []
    answers = []
    
    # Загружаем users
    with open('users.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            users[row['user_id']] = float(row['level_estimate']) if row['level_estimate'] else None
    
    # Загружаем sessions
    with open('sessions.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        sessions = list(reader)
    
    # Загружаем answers для анализа паттернов
    with open('answers.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        answers = list(reader)
    
    return users, sessions, answers

def get_next_ids(answers: List[Dict]) -> Tuple[int, int]:
    """Получает следующие ID для answer и session"""
    max_answer_id = 0
    max_session_id = 0
    
    for answer in answers:
        try:
            ans_num = int(answer['answer_id'].split('_')[1])
            max_answer_id = max(max_answer_id, ans_num)
        except:
            pass
        
        try:
            sess_num = int(answer['session_id'].split('_')[1])
            max_session_id = max(max_session_id, sess_num)
        except:
            pass
    
    return max_answer_id + 1, max_session_id + 1

def generate_part1_questions() -> List[Tuple[str, str]]:
    """Генерирует вопросы для Part 1"""
    questions = [
        ("q_part1_087", "Do you like listening to music?"),
        ("q_part1_088", "What kind of weather do you prefer?"),
        ("q_part1_089", "Do you enjoy watching TV?"),
        ("q_part1_090", "How do you usually spend your holidays?"),
        ("q_part1_091", "Do you prefer tea or coffee?"),
        ("q_part1_092", "What's your favorite season and why?"),
        ("q_part1_093", "Do you like going to the cinema?"),
        ("q_part1_094", "How often do you exercise?"),
        ("q_part1_095", "Do you enjoy shopping?"),
        ("q_part1_096", "What do you usually do on weekends?"),
        ("q_part1_097", "Do you prefer city or countryside?"),
        ("q_part1_098", "How do you relax after work?"),
        ("q_part1_099", "What's your favorite way to communicate?"),
        ("q_part1_100", "Do you like trying new things?"),
        ("q_part1_101", "What kind of food do you prefer?"),
        ("q_part1_102", "How often do you travel?"),
        ("q_part1_103", "Do you enjoy reading?"),
        ("q_part1_104", "What's your favorite hobby?"),
        ("q_part1_105", "Do you like animals?"),
        ("q_part1_106", "How do you stay healthy?"),
        ("q_part1_107", "Do you prefer mornings or evenings?"),
        ("q_part1_108", "How often do you use social media?"),
        ("q_part1_109", "Do you enjoy learning new languages?"),
        ("q_part1_110", "What's your favorite way to spend a weekend?"),
        ("q_part1_111", "Do you like watching sports?"),
        ("q_part1_112", "What kind of music do you listen to?"),
        ("q_part1_113", "Do you prefer working alone or in a team?"),
        ("q_part1_114", "How do you handle stress?"),
        ("q_part1_115", "What's your opinion on remote work?"),
        ("q_part1_116", "Do you enjoy traveling?"),
        ("q_part1_117", "What role does technology play in your life?"),
        ("q_part1_118", "How do you stay motivated?"),
        ("q_part1_119", "What's your favorite way to learn new things?"),
        ("q_part1_120", "Do you think it's important to have hobbies?"),
        ("q_part1_121", "How do you balance work and personal life?"),
    ]
    return questions

def generate_part1_answer(question: str, overall: float, fc: float, lr: float, gra: float, pr: float) -> Tuple[str, int]:
    """Генерирует ответ для Part 1 в зависимости от уровня"""
    duration = random.randint(10, 25)
    
    if overall <= 4.0:
        # Низкий уровень - простые ответы с ошибками
        templates = [
            f"I like {question.split()[-1].rstrip('?')}. It is good.",
            f"Yes, I like it. It is... um... nice.",
            f"I think... {question.split()[-1].rstrip('?')}... is good.",
            f"Yes, I do. I like it very much.",
        ]
        answer = random.choice(templates)
        
    elif overall <= 5.0:
        # Средний-низкий уровень
        templates = [
            f"Yes, I do like {question.split()[-1].rstrip('?')}. I think it is interesting and I enjoy it.",
            f"I really like {question.split()[-1].rstrip('?')}. It makes me happy and I do it often.",
            f"Yes, I enjoy {question.split()[-1].rstrip('?')}. It is one of my favorite things to do.",
        ]
        answer = random.choice(templates)
        
    elif overall <= 6.0:
        # Средний уровень
        templates = [
            f"Yes, I do enjoy {question.split()[-1].rstrip('?')}. I find it quite relaxing and it helps me unwind after a busy day.",
            f"I really like {question.split()[-1].rstrip('?')}. It's something I do regularly, especially on weekends when I have more free time.",
            f"Absolutely, I'm quite fond of {question.split()[-1].rstrip('?')}. I think it's a great way to spend my leisure time and I always look forward to it.",
        ]
        answer = random.choice(templates)
        
    elif overall <= 7.0:
        # Высокий уровень
        templates = [
            f"Yes, I absolutely enjoy {question.split()[-1].rstrip('?')}. I find it both intellectually stimulating and personally rewarding. It's become an integral part of my daily routine.",
            f"I'm quite passionate about {question.split()[-1].rstrip('?')}. I appreciate how it allows me to explore different perspectives and continuously learn new things.",
            f"Definitely, I'm very enthusiastic about {question.split()[-1].rstrip('?')}. It's something that brings me both relaxation and a sense of accomplishment.",
        ]
        answer = random.choice(templates)
        
    else:
        # Очень высокий уровень
        templates = [
            f"I have a genuine appreciation for {question.split()[-1].rstrip('?')}. It's become a fundamental aspect of how I approach life, offering both intellectual enrichment and personal fulfillment.",
            f"Absolutely, I'm deeply engaged with {question.split()[-1].rstrip('?')}. I find that it provides a unique combination of challenge and enjoyment that keeps me motivated.",
            f"Yes, I'm quite passionate about {question.split()[-1].rstrip('?')}. It's something I've cultivated over time, and it continues to be a source of both inspiration and satisfaction.",
        ]
        answer = random.choice(templates)
    
    return answer, duration

def generate_new_users(count: int, start_date: datetime) -> List[Dict]:
    """Генерирует новых пользователей"""
    new_users = []
    levels = [3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0]
    
    for i in range(count):
        user_id = f"550e8400-e29b-41d4-a716-44665544{4000+i:04d}"
        level = random.choice(levels)
        reg_date = start_date - timedelta(days=random.randint(1, 180))
        
        new_users.append({
            'user_id': user_id,
            'level_estimate': str(level),
            'registration_date': reg_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        })
    
    return new_users

def generate_new_sessions(users: List[str], count: int, start_date: datetime, start_session_id: int) -> List[Dict]:
    """Генерирует новые сессии"""
    new_sessions = []
    
    for i in range(count):
        session_id = f"sess_{start_session_id + i:03d}"
        user_id = random.choice(users)
        created_at = start_date - timedelta(days=random.randint(1, 90))
        
        # 50% имеют target_exam_date
        target_date = ""
        if random.random() < 0.5:
            target_date = (created_at + timedelta(days=random.randint(30, 120))).strftime('%Y-%m-%dT00:00:00Z')
        
        new_sessions.append({
            'session_id': session_id,
            'user_id': user_id,
            'created_at': created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'target_exam_date': target_date
        })
    
    return new_sessions

def main():
    print("=" * 70)
    print("SYNTHETIC EXPANSION: Part 1")
    print("=" * 70)
    
    # Загружаем существующие данные
    print("\n📂 Загрузка существующих данных...")
    users, sessions, answers = load_existing_data()
    print(f"   Загружено: {len(users)} пользователей, {len(sessions)} сессий, {len(answers)} ответов")
    
    # Получаем следующие ID
    next_answer_id, next_session_id = get_next_ids(answers)
    print(f"   Следующий answer_id: ans_{next_answer_id:03d}")
    print(f"   Следующий session_id: sess_{next_session_id:03d}")
    
    # Генерируем вопросы Part 1
    questions = generate_part1_questions()
    print(f"\n📝 Подготовлено {len(questions)} вопросов Part 1")
    
    # Генерируем новых пользователей (если нужно)
    existing_user_ids = list(users.keys())
    new_users_count = 20
    new_users = generate_new_users(new_users_count, datetime.now())
    print(f"\n👥 Генерируем {new_users_count} новых пользователей...")
    
    # Добавляем новых пользователей в users.csv
    with open('users.csv', 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['user_id', 'level_estimate', 'registration_date'])
        writer.writerows(new_users)
    
    all_user_ids = existing_user_ids + [u['user_id'] for u in new_users]
    all_users_dict = users.copy()
    for u in new_users:
        all_users_dict[u['user_id']] = float(u['level_estimate'])
    
    # Генерируем новые сессии
    sessions_needed = 150
    new_sessions = generate_new_sessions(all_user_ids, sessions_needed, datetime.now(), next_session_id)
    print(f"📅 Генерируем {sessions_needed} новых сессий...")
    
    # Добавляем новые сессии в sessions.csv
    with open('sessions.csv', 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['session_id', 'user_id', 'created_at', 'target_exam_date'])
        writer.writerows(new_sessions)
    
    # Генерируем ответы Part 1
    target_count = 600  # Целевое количество новых ответов Part 1
    print(f"\n📝 Генерируем {target_count} новых ответов Part 1...")
    
    new_answers = []
    band_distribution = {
        3.0: 2, 3.5: 15, 4.0: 50, 4.5: 20,
        5.0: 30, 5.5: 40, 6.0: 150, 6.5: 60,
        7.0: 100, 7.5: 80, 8.0: 40, 8.5: 13
    }
    
    question_idx = 0
    answer_id_counter = next_answer_id
    
    for overall, count in band_distribution.items():
        for _ in range(count):
            if question_idx >= len(questions):
                question_idx = 0
            
            q_id, q_text = questions[question_idx]
            question_idx += 1
            
            # Генерируем субскоры
            fc, lr, gra, pr = generate_realistic_subbands(overall)
            
            # Генерируем ответ (v2)
            answer_text, duration = generate_part1_answer_v2(q_text, overall, fc, lr, gra, pr)
            
            # Выбираем пользователя и сессию
            user_id = random.choice(all_user_ids)
            session_id = random.choice([s['session_id'] for s in new_sessions])
            
            # Определяем quality_flag
            quality_flag = determine_quality_flag(overall)
            
            # Создаем новый ответ
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
                'quality_flag': quality_flag
            }
            
            new_answers.append(new_answer)
            answer_id_counter += 1
    
    # Добавляем новые ответы в answers.csv
    print(f"\n💾 Сохранение {len(new_answers)} новых ответов...")
    with open('answers.csv', 'a', encoding='utf-8', newline='') as f:
        fieldnames = ['answer_id', 'session_id', 'user_id', 'part', 'question_id', 'question_text',
                     'answer_text', 'duration_sec', 'target_band_overall', 'target_band_fc',
                     'target_band_lr', 'target_band_gra', 'target_band_pr', 'transcript_raw',
                     'source_type', 'quality_flag']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(new_answers)
    
    # Статистика
    print("\n" + "=" * 70)
    print("✅ СТАТИСТИКА")
    print("=" * 70)
    print(f"   ✅ Добавлено пользователей: {len(new_users)}")
    print(f"   ✅ Добавлено сессий: {len(new_sessions)}")
    print(f"   ✅ Добавлено ответов Part 1: {len(new_answers)}")
    
    # Проверка разнообразия субскоров
    varied_3plus = sum(1 for a in new_answers if len(set([
        float(a['target_band_fc']), float(a['target_band_lr']),
        float(a['target_band_gra']), float(a['target_band_pr'])
    ])) >= 3)
    
    print(f"   ✅ Ответов с 3+ уникальными субскорами: {varied_3plus}/{len(new_answers)} ({varied_3plus/len(new_answers)*100:.1f}%)")
    
    print("\n✅ Part 1 expansion завершен!")

if __name__ == '__main__':
    main()

