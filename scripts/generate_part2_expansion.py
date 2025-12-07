#!/usr/bin/env python3
"""
Synthetic Expansion Script для Part 2
Генерация 400-600 новых ответов Part 2 с реалистичной структурой
"""

import csv
import random
from datetime import datetime, timedelta
from generate_synthetic_expansion import round_to_half, generate_realistic_subbands, load_existing_data, get_next_ids, generate_new_sessions, generate_new_users
from improved_generation_v2 import generate_part2_answer_v2
from improve_generation import determine_quality_flag

def generate_part2_questions() -> list:
    """Генерирует вопросы для Part 2"""
    questions = [
        ("q_part2_077", "Describe a memorable journey you took."),
        ("q_part2_078", "Describe a place where you feel most creative."),
        ("q_part2_079", "Describe a time when you had to adapt to a new situation."),
        ("q_part2_080", "Describe a moment when you felt truly grateful."),
        ("q_part2_081", "Describe a skill you'd like to develop."),
        ("q_part2_082", "Describe a piece of technology you use daily."),
        ("q_part2_083", "Describe a mistake you learned from."),
        ("q_part2_084", "Describe a friend who is important to you."),
        ("q_part2_085", "Describe a goal you want to achieve."),
        ("q_part2_086", "Describe a hobby you enjoy."),
        ("q_part2_087", "Describe a movie you recently watched."),
        ("q_part2_088", "Describe a book that influenced you deeply."),
        ("q_part2_089", "Describe a celebration you attended."),
        ("q_part2_090", "Describe a time you were proud of yourself."),
        ("q_part2_091", "Describe a change you made in your life."),
        ("q_part2_092", "Describe a place you'd love to visit."),
        ("q_part2_093", "Describe an achievement you're most proud of."),
        ("q_part2_094", "Describe a piece of music that moves you."),
        ("q_part2_095", "Describe a decision that shaped your life."),
        ("q_part2_096", "Describe a time when you overcame a significant challenge."),
        ("q_part2_097", "Describe a teacher who influenced you."),
        ("q_part2_098", "Describe a place that holds special meaning for you."),
        ("q_part2_099", "Describe a person who has significantly influenced your thinking."),
        ("q_part2_100", "Describe an experience that taught you about resilience."),
    ]
    return questions

def generate_part2_answer(question: str, overall: float) -> tuple:
    """Генерирует ответ для Part 2 в зависимости от уровня"""
    duration = random.randint(45, 70)
    
    # Извлекаем тему из вопроса
    topic = question.lower().replace("describe ", "").replace("a ", "").replace("an ", "").split()[0:3]
    topic_str = " ".join(topic)
    
    if overall <= 4.0:
        # Низкий уровень - простые ответы с ошибками
        answer = f"I want to talk about {topic_str}. It was... um... good. I like it. It was... nice. I remember... it was last year. I was happy. It was good experience. I like it very much."
        
    elif overall <= 5.0:
        # Средний-низкий уровень
        answer = f"I'd like to describe {topic_str}. It happened last year. I remember it was very interesting. I enjoyed it a lot. What I liked most was that it was fun and I had good time. I think it was important experience for me. I learned something from it."
        
    elif overall <= 6.0:
        # Средний уровень
        answer = f"I'd like to talk about {topic_str}. This was something that happened about a year ago, and it left a strong impression on me. What made it particularly memorable was the way it challenged my expectations and opened up new perspectives. I remember feeling both excited and a bit nervous at first, but as things progressed, I found myself really enjoying the experience. What I appreciated most was how it taught me something valuable about myself and my capabilities. Looking back, I realize this experience has influenced how I approach similar situations today."
        
    elif overall <= 7.0:
        # Высокий уровень
        answer = f"I'd like to describe {topic_str}, which has been a significant experience in my life. This occurred approximately two years ago, and it fundamentally changed how I understand certain aspects of life. What made it particularly meaningful was the combination of challenge and growth it presented. I remember the initial period was quite demanding, requiring me to step outside my comfort zone and adapt to new circumstances. However, as I navigated through the experience, I discovered strengths and capabilities I hadn't recognized before. What I found most valuable was how it taught me about resilience, adaptability, and the importance of maintaining perspective during difficult times. This experience continues to influence my decisions and approach to new challenges, and I'm grateful for the insights it provided."
        
    else:
        # Очень высокий уровень
        answer = f"I'd like to describe {topic_str}, which represents one of the most transformative experiences I've had. This occurred about three years ago, and it fundamentally reshaped my understanding of both myself and the world around me. What made it particularly profound was the way it combined intellectual challenge with emotional growth, requiring me to engage deeply with complex questions and navigate uncertainty. I remember the initial phase was quite intense, as I had to confront assumptions I'd held for years and adapt to perspectives that were initially uncomfortable. However, as I immersed myself in the experience, I began to appreciate its transformative potential. What I found most valuable was how it taught me about the importance of intellectual humility, the value of sustained effort in the face of difficulty, and the ways in which challenging experiences can become sources of strength and wisdom. This experience has become a touchstone for how I approach learning, growth, and engagement with complex issues, and I continue to draw on the insights and resilience it helped me develop."
    
    return answer, duration

def main():
    print("=" * 70)
    print("SYNTHETIC EXPANSION: Part 2")
    print("=" * 70)
    
    # Загружаем существующие данные
    print("\n📂 Загрузка существующих данных...")
    users, sessions, answers = load_existing_data()
    print(f"   Загружено: {len(users)} пользователей, {len(sessions)} сессий, {len(answers)} ответов")
    
    # Получаем следующие ID
    next_answer_id, next_session_id = get_next_ids(answers)
    print(f"   Следующий answer_id: ans_{next_answer_id:03d}")
    print(f"   Следующий session_id: sess_{next_session_id:03d}")
    
    # Генерируем вопросы Part 2
    questions = generate_part2_questions()
    print(f"\n📝 Подготовлено {len(questions)} вопросов Part 2")
    
    # Получаем всех пользователей
    with open('users.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_users = list(reader)
    
    all_user_ids = [u['user_id'] for u in all_users]
    
    # Получаем все сессии
    with open('sessions.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_sessions = list(reader)
    
    # Генерируем ответы Part 2
    target_count = 500  # Целевое количество новых ответов Part 2
    print(f"\n📝 Генерируем {target_count} новых ответов Part 2...")
    
    new_answers = []
    band_distribution = {
        3.5: 10, 4.0: 40, 4.5: 20,
        5.0: 40, 5.5: 50, 6.0: 120, 6.5: 60,
        7.0: 80, 7.5: 60, 8.0: 15, 8.5: 5
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
            answer_text, duration = generate_part2_answer_v2(q_text, overall, fc, lr, gra, pr)
            
            # Выбираем пользователя и сессию
            user_id = random.choice(all_user_ids)
            session_id = random.choice([s['session_id'] for s in all_sessions])
            
            # Определяем quality_flag
            quality_flag = determine_quality_flag(overall)
            
            # Создаем новый ответ
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
    print(f"   ✅ Добавлено ответов Part 2: {len(new_answers)}")
    
    # Проверка разнообразия субскоров
    varied_3plus = sum(1 for a in new_answers if len(set([
        float(a['target_band_fc']), float(a['target_band_lr']),
        float(a['target_band_gra']), float(a['target_band_pr'])
    ])) >= 3)
    
    print(f"   ✅ Ответов с 3+ уникальными субскорами: {varied_3plus}/{len(new_answers)} ({varied_3plus/len(new_answers)*100:.1f}%)")
    
    print("\n✅ Part 2 expansion завершен!")

if __name__ == '__main__':
    main()

