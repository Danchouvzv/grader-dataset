#!/usr/bin/env python3
"""
Скрипт для улучшения датасета:
1. Добавляет реалистичный разброс субскоров вокруг overall
2. Добавляет новые поля: transcript_raw, source_type, quality_flag
3. Добавляет вариацию ±1.0 band вокруг level_estimate пользователя
"""

import csv
import random
import math
from typing import Dict, List, Tuple

random.seed(42)

def round_to_half(n: float) -> float:
    """Округляет до ближайшего 0.5"""
    return round(n * 2) / 2

def generate_realistic_subbands(overall: float, user_level: float) -> Tuple[float, float, float, float]:
    """
    Генерирует реалистичные субскоры вокруг overall.
    
    Правила:
    - У слабых уровней (4.0-5.5) чаще проседают GRA/PR
    - У сильных (7.0+) выше LR/FC
    - У русскоязычных часто LR > GRA
    - PR часто отстает от других
    """
    # Для слабых уровней
    if overall <= 5.0:
        # Чаще проседают GRA и PR
        gra_offset = random.choice([-0.5, -0.5, 0, 0])
        pr_offset = random.choice([-0.5, -0.5, 0, 0.5])
        lr_offset = random.choice([-0.5, 0, 0, 0.5])  # LR может быть выше
        fc_offset = random.choice([-0.5, 0, 0, 0])
    elif overall <= 6.5:
        # Средний уровень - более равномерный разброс
        gra_offset = random.choice([-0.5, 0, 0, 0.5])
        pr_offset = random.choice([-0.5, 0, 0, 0.5])
        lr_offset = random.choice([-0.5, 0, 0.5, 0.5])  # LR часто выше
        fc_offset = random.choice([-0.5, 0, 0, 0.5])
    else:  # 7.0+
        # Сильные уровни - LR и FC часто выше
        gra_offset = random.choice([-0.5, 0, 0, 0.5])
        pr_offset = random.choice([-0.5, 0, 0, 0.5])
        lr_offset = random.choice([0, 0, 0.5, 0.5])  # LR часто выше
        fc_offset = random.choice([0, 0, 0.5, 0.5])  # FC часто выше
    
    fc = round_to_half(overall + fc_offset)
    lr = round_to_half(overall + lr_offset)
    gra = round_to_half(overall + gra_offset)
    pr = round_to_half(overall + pr_offset)
    
    # Ограничиваем диапазон 3.0-9.0
    fc = max(3.0, min(9.0, fc))
    lr = max(3.0, min(9.0, lr))
    gra = max(3.0, min(9.0, gra))
    pr = max(3.0, min(9.0, pr))
    
    return fc, lr, gra, pr

def add_variation_to_overall(overall: float, user_level: float) -> float:
    """
    Добавляет вариацию вокруг level_estimate пользователя.
    Для близких к уровню ответов: небольшая вариация ±0.5.
    """
    # Разброс зависит от того, насколько overall близок к user_level
    if abs(overall - user_level) < 0.5:
        # Если уже близко к уровню пользователя, добавляем небольшую вариацию
        variation = random.choice([-0.5, 0, 0.5])
    else:
        # Если далеко, оставляем как есть (это уже "плохой день" или "хороший день")
        variation = 0
    
    new_overall = round_to_half(overall + variation)
    return max(3.0, min(9.0, new_overall))

def determine_quality_flag(answer_text: str, overall: float) -> str:
    """
    Определяет quality_flag на основе текста и уровня.
    
    Правила:
    - Очень короткие ответы (< 5 слов) → garbage
    - Много не-алфавитных токенов → garbage
    - Пустые или только междометия → garbage
    """
    words = answer_text.split()
    word_count = len(words)
    
    # Очень короткие ответы
    if word_count < 5:
        return 'garbage'
    
    # Проверяем долю не-алфавитных токенов (только междометия, точки и т.д.)
    non_alpha_ratio = sum(1 for w in words if not any(c.isalpha() for c in w)) / max(word_count, 1)
    if non_alpha_ratio > 0.5:
        return 'garbage'
    
    # Пустые или почти пустые
    if not answer_text.strip() or len(answer_text.strip()) < 3:
        return 'garbage'
    
    # Для низких уровней дополнительные проверки
    if overall <= 4.0:
        # Много пауз и обрывков
        if answer_text.count('...') > 2 or (answer_text.lower() == answer_text and word_count < 8):
            return 'garbage'
    
    return 'ok'

def enhance_answers():
    """Основная функция для улучшения датасета"""
    
    # Читаем users для получения level_estimate
    users = {}
    with open('users.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            users[row['user_id']] = float(row['level_estimate']) if row['level_estimate'] else None
    
    # Читаем answers
    answers = []
    with open('answers.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            answers.append(row)
    
    # Обрабатываем каждый ответ
    enhanced_answers = []
    for answer in answers:
        # Пропускаем garbage-ответы (не трогаем их, чтобы сохранить стабильность)
        if answer.get('quality_flag') == 'garbage':
            # Убеждаемся, что все поля есть
            if 'transcript_raw' not in answer:
                answer['transcript_raw'] = answer['answer_text']
            if 'source_type' not in answer:
                answer['source_type'] = 'synthetic'
            enhanced_answers.append(answer)
            continue
        
        overall = float(answer['target_band_overall'])
        user_id = answer['user_id']
        user_level = users.get(user_id)
        
        # Обрабатываем случай, когда user_level может быть None
        if user_level is None:
            user_level = overall
        
        # Добавляем вариацию к overall (если нужно)
        # Для части ответов оставляем как есть, для части добавляем вариацию
        if random.random() < 0.3:  # 30% ответов получают вариацию
            overall = add_variation_to_overall(overall, user_level)
        
        # Генерируем реалистичные субскоры
        fc, lr, gra, pr = generate_realistic_subbands(overall, user_level)
        
        # Обновляем ответ
        answer['target_band_overall'] = str(overall)
        answer['target_band_fc'] = str(fc)
        answer['target_band_lr'] = str(lr)
        answer['target_band_gra'] = str(gra)
        answer['target_band_pr'] = str(pr)
        
        # Добавляем новые поля (если их еще нет)
        if 'transcript_raw' not in answer:
            answer['transcript_raw'] = answer['answer_text']  # Пока одинаковые, потом можно добавить ASR-шум
        if 'source_type' not in answer:
            answer['source_type'] = 'synthetic'
        if 'quality_flag' not in answer:
            answer['quality_flag'] = determine_quality_flag(answer['answer_text'], overall)
        
        enhanced_answers.append(answer)
    
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
        writer.writerows(enhanced_answers)
    
    print(f"✅ Обновлено {len(enhanced_answers)} ответов")
    print("✅ Добавлены поля: transcript_raw, source_type, quality_flag")
    print("✅ Добавлен реалистичный разброс субскоров")

if __name__ == '__main__':
    enhance_answers()

