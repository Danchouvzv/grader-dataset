#!/usr/bin/env python3
"""
Synthetic Expansion Script для Part 3
Генерация 300-450 новых ответов Part 3 с расширенными темами
"""

import csv
import random
from datetime import datetime, timedelta
from generate_synthetic_expansion import round_to_half, generate_realistic_subbands, load_existing_data, get_next_ids
from error_injection import inject_errors_by_subscores
from improve_generation import determine_quality_flag

def generate_part3_questions() -> list:
    """Генерирует вопросы для Part 3 с расширенными темами"""
    questions = [
        # Education
        ("q_part3_079", "How important is education in modern society?"),
        ("q_part3_080", "Do you think online education can replace traditional classrooms?"),
        ("q_part3_081", "What role should teachers play in students' lives?"),
        ("q_part3_082", "Is university education necessary for success?"),
        
        # Technology
        ("q_part3_083", "How will artificial intelligence change our lives?"),
        ("q_part3_084", "What are the negative effects of social media?"),
        ("q_part3_085", "Should governments regulate technology companies?"),
        ("q_part3_086", "How has technology affected human relationships?"),
        
        # Society
        ("q_part3_087", "What are the challenges of an aging population?"),
        ("q_part3_088", "How can we reduce social inequality?"),
        ("q_part3_089", "What makes a strong community?"),
        ("q_part3_090", "How has urbanization changed society?"),
        
        # Environment
        ("q_part3_091", "What can individuals do to protect the environment?"),
        ("q_part3_092", "Should governments prioritize economic growth or environmental protection?"),
        ("q_part3_093", "How can we encourage sustainable living?"),
        ("q_part3_094", "What are the consequences of climate change?"),
        
        # Globalization
        ("q_part3_095", "How does globalization affect local cultures?"),
        ("q_part3_096", "What are the benefits and drawbacks of globalization?"),
        ("q_part3_097", "Should countries protect their local industries?"),
        ("q_part3_098", "How has globalization changed the way we work?"),
        
        # Psychology
        ("q_part3_099", "Why do people experience stress?"),
        ("q_part3_100", "How important is work-life balance?"),
        ("q_part3_101", "What factors motivate people?"),
        ("q_part3_102", "How can we improve mental health awareness?"),
        
        # Work & Employment
        ("q_part3_103", "How will automation affect jobs?"),
        ("q_part3_104", "What makes a job satisfying?"),
        ("q_part3_105", "Should people change careers frequently?"),
        ("q_part3_106", "How has remote work changed employment?"),
        
        # Culture
        ("q_part3_107", "How can we preserve traditional culture?"),
        ("q_part3_108", "What is the value of cultural diversity?"),
        ("q_part3_109", "How does tourism affect local culture?"),
        ("q_part3_110", "Should cultures change to adapt to modern times?"),
        
        # Family & Relationships
        ("q_part3_111", "How have family structures changed?"),
        ("q_part3_112", "What makes a good parent?"),
        ("q_part3_113", "How do generational differences affect relationships?"),
        ("q_part3_114", "What is the importance of family in modern society?"),
        
        # Economics
        ("q_part3_115", "How does consumerism affect society?"),
        ("q_part3_116", "What causes economic inequality?"),
        ("q_part3_117", "Should governments support small businesses?"),
        ("q_part3_118", "How important is entrepreneurship?"),
        
        # Urbanization
        ("q_part3_119", "What are the challenges of city life?"),
        ("q_part3_120", "How can cities become more sustainable?"),
        ("q_part3_121", "What attracts people to cities?"),
        ("q_part3_122", "How can we improve urban planning?"),
        
        # Ethics
        ("q_part3_123", "How should we balance privacy and security?"),
        ("q_part3_124", "What are the ethical implications of AI?"),
        ("q_part3_125", "Should animal rights be protected?"),
        ("q_part3_126", "What are the ethical challenges in medicine?"),
    ]
    return questions

def generate_part3_answer(question: str, overall: float, fc: float, lr: float, gra: float, pr: float) -> tuple:
    """Генерирует ответ для Part 3 с улучшенной вариативностью"""
    # Используем улучшенную версию
    from generate_part3_expansion_v2 import generate_part3_answer_v2
    return generate_part3_answer_v2(question, overall, fc, lr, gra, pr)

def main():
    print("=" * 70)
    print("SYNTHETIC EXPANSION: Part 3")
    print("=" * 70)
    
    # Загружаем существующие данные
    print("\n📂 Загрузка существующих данных...")
    users, sessions, answers = load_existing_data()
    print(f"   Загружено: {len(users)} пользователей, {len(sessions)} сессий, {len(answers)} ответов")
    
    # Получаем следующие ID
    next_answer_id, next_session_id = get_next_ids(answers)
    print(f"   Следующий answer_id: ans_{next_answer_id:03d}")
    print(f"   Следующий session_id: sess_{next_session_id:03d}")
    
    # Генерируем вопросы Part 3
    questions = generate_part3_questions()
    print(f"\n📝 Подготовлено {len(questions)} вопросов Part 3")
    
    # Получаем всех пользователей и сессии
    with open('users.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_users = list(reader)
    
    all_user_ids = [u['user_id'] for u in all_users]
    
    with open('sessions.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_sessions = list(reader)
    
    # Генерируем ответы Part 3
    target_count = 400  # Целевое количество новых ответов Part 3
    print(f"\n📝 Генерируем {target_count} новых ответов Part 3...")
    
    new_answers = []
    band_distribution = {
        3.5: 8, 4.0: 30, 4.5: 15,
        5.0: 30, 5.5: 40, 6.0: 100, 6.5: 50,
        7.0: 70, 7.5: 45, 8.0: 10, 8.5: 2
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
            
            # Генерируем ответ
            answer_text, duration = generate_part3_answer(q_text, overall, fc, lr, gra, pr)
            
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
                'part': '3',
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
    print(f"   ✅ Добавлено ответов Part 3: {len(new_answers)}")
    
    # Проверка разнообразия субскоров
    varied_3plus = sum(1 for a in new_answers if len(set([
        float(a['target_band_fc']), float(a['target_band_lr']),
        float(a['target_band_gra']), float(a['target_band_pr'])
    ])) >= 3)
    
    print(f"   ✅ Ответов с 3+ уникальными субскорами: {varied_3plus}/{len(new_answers)} ({varied_3plus/len(new_answers)*100:.1f}%)")
    
    print("\n✅ Part 3 expansion завершен!")

if __name__ == '__main__':
    main()

