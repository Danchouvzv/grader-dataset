#!/usr/bin/env python3
"""
Добавляет 30 "убитых" ответов уровня 3.5-4.5 с максимально корявыми текстами.

ВАЖНО: Запускать ПОСЛЕ enhance_dataset.py, чтобы не перезаписывать
уже обработанные ответы.
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

# Список очень корявых ответов Part 1
trash_answers = [
    {
        'question': "Do you work or study?",
        'answer': "work study... sometimes... no job now... home... looking job... internet",
        'overall': 4.0,
        'fc': 3.5,
        'lr': 4.0,
        'gra': 3.5,
        'pr': 4.0,
        'duration': 8
    },
    {
        'question': "Where are you from?",
        'answer': "i from... russia... city... big... many people... i like",
        'overall': 3.5,
        'fc': 3.5,
        'lr': 3.5,
        'gra': 3.0,
        'pr': 4.0,
        'duration': 7
    },
    {
        'question': "What do you like to do in your free time?",
        'answer': "free time... i... watch... tv... play... games... computer... sometimes... walk",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 9
    },
    {
        'question': "Do you enjoy cooking?",
        'answer': "no... i not cook... mother cook... i eat... restaurant sometimes",
        'overall': 3.5,
        'fc': 3.5,
        'lr': 3.5,
        'gra': 3.0,
        'pr': 4.0,
        'duration': 8
    },
    {
        'question': "How do you usually spend your weekends?",
        'answer': "weekend... sleep... late... then... maybe... shopping... or... nothing... stay home",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 10
    },
    {
        'question': "What kind of music do you like?",
        'answer': "music... pop... rock... i listen... every day... phone... when... go work",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 4.0,
        'gra': 3.5,
        'pr': 4.5,
        'duration': 9
    },
    {
        'question': "Where do you live?",
        'answer': "i live... apartment... small... one room... kitchen... bathroom... ok",
        'overall': 3.5,
        'fc': 3.5,
        'lr': 3.5,
        'gra': 3.0,
        'pr': 4.0,
        'duration': 8
    },
    {
        'question': "Do you work or study?",
        'answer': "i study... university... second year... computer... very difficult... many... exams... homework",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 11
    },
    {
        'question': "What's your favorite food?",
        'answer': "food... i like... pizza... pasta... burger... fast food... sometimes... cook... simple",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 4.0,
        'gra': 3.5,
        'pr': 4.5,
        'duration': 10
    },
    {
        'question': "How often do you exercise?",
        'answer': "exercise... no... sometimes... walk... not often... busy... work... study",
        'overall': 3.5,
        'fc': 3.5,
        'lr': 3.5,
        'gra': 3.0,
        'pr': 4.0,
        'duration': 9
    },
    {
        'question': "What is your full name?",
        'answer': "my name... is... dmitry... dmitry ivanov... that's... all",
        'overall': 3.5,
        'fc': 3.5,
        'lr': 3.5,
        'gra': 3.0,
        'pr': 4.0,
        'duration': 6
    },
    {
        'question': "Do you like sports?",
        'answer': "sports... yes... football... basketball... i play... sometimes... with friends... weekend",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 9
    },
    {
        'question': "How do you get to work or school?",
        'answer': "i go... metro... every day... fast... cheap... sometimes... bus... if... metro... broken",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 10
    },
    {
        'question': "What's your favorite season?",
        'answer': "season... i like... summer... warm... can go... beach... swimming... sun... good",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 9
    },
    {
        'question': "Do you enjoy shopping?",
        'answer': "shopping... yes... sometimes... clothes... food... supermarket... online... also",
        'overall': 3.5,
        'fc': 3.5,
        'lr': 3.5,
        'gra': 3.0,
        'pr': 4.0,
        'duration': 8
    },
    {
        'question': "What do you do in the evenings?",
        'answer': "evening... i... watch... tv... or... read... sometimes... cook... dinner... talk... family",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 10
    },
    {
        'question': "Do you prefer city life or country life?",
        'answer': "city... i like... city... many... shops... restaurants... people... interesting... country... quiet... boring",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 11
    },
    {
        'question': "How long have you been studying English?",
        'answer': "english... i study... three... years... school... then... university... still... learning... difficult",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 10
    },
    {
        'question': "What's the weather like in your country?",
        'answer': "weather... cold... winter... snow... summer... warm... sometimes... rain... spring... autumn... ok",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 11
    },
    {
        'question': "Do you have any hobbies?",
        'answer': "hobbies... yes... photography... take... pictures... nature... city... also... play... guitar... sometimes",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 10
    },
    {
        'question': "What kind of books do you read?",
        'answer': "books... fiction... mystery... sometimes... history... not often... prefer... movies... easier",
        'overall': 3.5,
        'fc': 3.5,
        'lr': 3.5,
        'gra': 3.0,
        'pr': 4.0,
        'duration': 9
    },
    {
        'question': "How do you relax after a long day?",
        'answer': "relax... music... listen... or... watch... netflix... sometimes... bath... hot... water... good",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 10
    },
    {
        'question': "Do you prefer staying home or going out?",
        'answer': "home... i like... stay... home... comfortable... safe... going out... sometimes... friends... weekend",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 10
    },
    {
        'question': "What's your favorite way to communicate?",
        'answer': "communicate... phone... message... whatsapp... sometimes... call... video... zoom... work",
        'overall': 3.5,
        'fc': 3.5,
        'lr': 3.5,
        'gra': 3.0,
        'pr': 4.0,
        'duration': 9
    },
    {
        'question': "Do you live in a house or apartment?",
        'answer': "apartment... small... two rooms... kitchen... bathroom... balcony... ok... comfortable",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 9
    },
    {
        'question': "What do you like about your hometown?",
        'answer': "hometown... nice... people... friendly... many... shops... restaurants... parks... i like",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 10
    },
    {
        'question': "Do you enjoy traveling?",
        'answer': "traveling... yes... i like... visit... different... cities... countries... see... new... places... interesting",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 11
    },
    {
        'question': "What's your favorite type of cuisine?",
        'answer': "cuisine... italian... pizza... pasta... also... japanese... sushi... ramen... spicy... good",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 10
    },
    {
        'question': "How do you usually travel?",
        'answer': "travel... train... long... trips... plane... far... countries... car... short... trips... city... metro",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 11
    },
    {
        'question': "What do you do for a living?",
        'answer': "work... office... accountant... numbers... computer... excel... sometimes... boring... but... ok... money... good",
        'overall': 4.0,
        'fc': 4.0,
        'lr': 3.5,
        'gra': 4.0,
        'pr': 4.0,
        'duration': 12
    }
]

def add_trash_answers():
    """Добавляет убитые ответы в датасет"""
    
    # Читаем существующие ответы
    with open('answers.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        existing_answers = list(reader)
    
    # Находим максимальный answer_id
    max_id = 0
    for answer in existing_answers:
        try:
            num = int(answer['answer_id'].split('_')[1])
            max_id = max(max_id, num)
        except:
            pass
    
    # Читаем users для получения слабых пользователей (3.5-4.5)
    with open('users.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        weak_users = []
        for row in reader:
            level = float(row['level_estimate']) if row['level_estimate'] else None
            if level and 3.5 <= level <= 4.5:
                weak_users.append(row['user_id'])
    
    # Если слабых пользователей мало, создаем еще
    if len(weak_users) < 10:
        # Добавляем еще слабых пользователей
        new_users = []
        with open('users.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            users_data = list(reader)
        
        for i in range(10):
            user_id = f"550e8400-e29b-41d4-a716-44665544{3000+i:04d}"
            reg_date = (datetime.now() - timedelta(days=random.randint(1, 90))).replace(microsecond=0)
            new_users.append({
                'user_id': user_id,
                'level_estimate': str(round(random.uniform(3.5, 4.5) * 2) / 2),
                'registration_date': reg_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            })
            weak_users.append(user_id)
        
        # Добавляем новых пользователей
        with open('users.csv', 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['user_id', 'level_estimate', 'registration_date']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users_data)
            writer.writerows(new_users)
    
    # Читаем sessions
    with open('sessions.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        sessions = list(reader)
    
    # Создаем новые сессии для слабых пользователей если нужно
    max_sess = 0
    for sess in sessions:
        try:
            num = int(sess['session_id'].split('_')[1])
            max_sess = max(max_sess, num)
        except:
            pass
    
    # Генерируем новые ответы
    new_answers = []
    for i, trash in enumerate(trash_answers[:30]):  # Берем первые 30
        answer_id = f"ans_{max_id + 1 + i:03d}"
        
        # Выбираем случайного слабого пользователя
        user_id = random.choice(weak_users)
        
        # Находим или создаем сессию для этого пользователя
        user_sessions = [s for s in sessions if s['user_id'] == user_id]
        if not user_sessions:
            # Создаем новую сессию
            session_id = f"sess_{max_sess + 1 + i:03d}"
            sess_date = (datetime.now() - timedelta(days=random.randint(1, 30))).replace(microsecond=0)
            sessions.append({
                'session_id': session_id,
                'user_id': user_id,
                'created_at': sess_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'target_exam_date': ''
            })
        else:
            session_id = random.choice(user_sessions)['session_id']
        
        question_id = f"q_part1_{100 + i:03d}"
        
        new_answer = {
            'answer_id': answer_id,
            'session_id': session_id,
            'user_id': user_id,
            'part': '1',
            'question_id': question_id,
            'question_text': trash['question'],
            'answer_text': trash['answer'],
            'duration_sec': str(trash['duration']),
            'target_band_overall': str(trash['overall']),
            'target_band_fc': str(trash['fc']),
            'target_band_lr': str(trash['lr']),
            'target_band_gra': str(trash['gra']),
            'target_band_pr': str(trash['pr']),
            'transcript_raw': trash['answer'],
            'source_type': 'synthetic',
            'quality_flag': 'garbage'
        }
        new_answers.append(new_answer)
    
    # Добавляем новые ответы к существующим
    all_answers = existing_answers + new_answers
    
    # Записываем обратно
    fieldnames = [
        'answer_id', 'session_id', 'user_id', 'part', 'question_id', 'question_text',
        'answer_text', 'duration_sec', 'target_band_overall', 'target_band_fc',
        'target_band_lr', 'target_band_gra', 'target_band_pr',
        'transcript_raw', 'source_type', 'quality_flag'
    ]
    
    with open('answers.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_answers)
    
    # Обновляем sessions
    with open('sessions.csv', 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['session_id', 'user_id', 'created_at', 'target_exam_date']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sessions)
    
    print(f"✅ Добавлено {len(new_answers)} убитых ответов уровня 3.5-4.5")
    print("✅ Добавлены новые слабые пользователи если нужно")

if __name__ == '__main__':
    add_trash_answers()

