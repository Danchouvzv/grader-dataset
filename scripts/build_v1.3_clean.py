#!/usr/bin/env python3
"""
Сборка v1.3 - Clean & Validated Dataset
- Удаляет проблемные ответы
- Регенерирует через улучшенные генераторы
- Добавляет low-band data
- Балансирует части
"""

import csv
import random
import os
import shutil
from collections import defaultdict
from generate_part1_v2_clean import generate_part1_answer_v2_clean
from generate_part2_v2_clean import generate_part2_answer_v2_clean
from generate_part3_expansion_v2 import generate_part3_answer_v2
from generate_synthetic_expansion import generate_realistic_subbands
from improve_generation import determine_quality_flag
from validate_and_filter import validate_part1, validate_part2, validate_part3

def load_validation_results():
    """Загружает результаты валидации"""
    results = {}
    with open('docs/validation_results_v1.3.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results[row['answer_id']] = row
    return results

def load_answers(filepath: str):
    """Загружает ответы"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def generate_low_band_data(count: int, part: str) -> list:
    """Генерирует дополнительные low-band ответы"""
    from generate_synthetic_expansion import generate_part1_questions
    from generate_part2_expansion import generate_part2_questions
    from generate_part3_expansion import generate_part3_questions
    
    new_answers = []
    
    if part == '1':
        questions = generate_part1_questions()
    elif part == '2':
        questions = generate_part2_questions()
    else:
        questions = generate_part3_questions()
    
    # Загружаем существующих пользователей и сессии
    with open('dataset_versions/v1.2/users.csv', 'r', encoding='utf-8') as f:
        users = list(csv.DictReader(f))
    with open('dataset_versions/v1.2/sessions.csv', 'r', encoding='utf-8') as f:
        sessions = list(csv.DictReader(f))
    
    user_ids = [u['user_id'] for u in users]
    session_ids = [s['session_id'] for s in sessions]
    
    # Генерируем low-band ответы (4.0-5.0)
    bands = [4.0, 4.5, 5.0]
    
    for i in range(count):
        overall = random.choice(bands)
        fc, lr, gra, pr = generate_realistic_subbands(overall)
        
        q_id, q_text = random.choice(questions)
        
        if part == '1':
            answer_text, duration = generate_part1_answer_v2_clean(q_text, overall, fc, lr, gra, pr)
        elif part == '2':
            answer_text, duration = generate_part2_answer_v2_clean(q_text, overall, fc, lr, gra, pr)
        else:
            answer_text, duration = generate_part3_answer_v2(q_text, overall, fc, lr, gra, pr)
        
        # Находим максимальный answer_id
        max_id = 0
        # Будем использовать простую нумерацию
        answer_id = f'ans_{4022 + i + 1:04d}'
        
        new_answer = {
            'answer_id': answer_id,
            'session_id': random.choice(session_ids),
            'user_id': random.choice(user_ids),
            'part': part,
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
            'source_type': 'synthetic_v1.3_low_band',
            'quality_flag': determine_quality_flag(overall)
        }
        
        new_answers.append(new_answer)
    
    return new_answers

def main():
    print("=" * 70)
    print("СБОРКА V1.3: CLEAN & VALIDATED DATASET")
    print("=" * 70)
    
    # Загружаем v1.2
    print("\n📂 Загрузка v1.2...")
    answers = load_answers('dataset_versions/v1.2/answers.csv')
    print(f"   Загружено: {len(answers)} ответов")
    
    # Загружаем результаты валидации
    print("\n📋 Загрузка результатов валидации...")
    validation = load_validation_results()
    print(f"   Загружено: {len(validation)} результатов")
    
    # Разделяем на категории
    to_keep = []
    to_regenerate = []
    to_delete = []
    
    for answer in answers:
        answer_id = answer.get('answer_id')
        if answer_id not in validation:
            to_keep.append(answer)
            continue
        
        action = validation[answer_id]['action']
        if action == 'keep':
            to_keep.append(answer)
        elif action == 'regenerate':
            to_regenerate.append(answer)
        elif action == 'delete':
            to_delete.append(answer)
    
    print(f"\n📊 КАТЕГОРИИ:")
    print(f"   ✅ Keep: {len(to_keep)}")
    print(f"   🔄 Regenerate: {len(to_regenerate)}")
    print(f"   🗑️  Delete: {len(to_delete)}")
    
    # Регенерируем
    print(f"\n🔄 Регенерация {len(to_regenerate)} ответов...")
    regenerated = []
    
    random.seed(42)
    for old_answer in to_regenerate:
        try:
            part = old_answer.get('part', '')
            overall = float(old_answer.get('target_band_overall', 0))
            fc = float(old_answer.get('target_band_fc', 0))
            lr = float(old_answer.get('target_band_lr', 0))
            gra = float(old_answer.get('target_band_gra', 0))
            pr = float(old_answer.get('target_band_pr', 0))
            
            question_text = old_answer.get('question_text', '')
            
            if part == '1':
                answer_text, duration = generate_part1_answer_v2_clean(question_text, overall, fc, lr, gra, pr)
            elif part == '2':
                answer_text, duration = generate_part2_answer_v2_clean(question_text, overall, fc, lr, gra, pr)
            elif part == '3':
                answer_text, duration = generate_part3_answer_v2(question_text, overall, fc, lr, gra, pr)
            else:
                continue
            
            new_answer = old_answer.copy()
            new_answer['answer_text'] = answer_text
            new_answer['transcript_raw'] = answer_text
            new_answer['duration_sec'] = str(duration)
            new_answer['source_type'] = 'synthetic_v1.3'
            new_answer['quality_flag'] = determine_quality_flag(overall)
            
            regenerated.append(new_answer)
            
        except Exception as e:
            print(f"   ⚠️  Ошибка при регенерации {old_answer.get('answer_id')}: {e}")
            # Оставляем старый ответ
            to_keep.append(old_answer)
    
    print(f"   ✅ Регенерировано: {len(regenerated)}")
    
    # Добавляем low-band data
    print(f"\n➕ Генерация дополнительных low-band ответов...")
    low_band_p1 = generate_low_band_data(100, '1')
    low_band_p2 = generate_low_band_data(50, '2')
    low_band_p3 = generate_low_band_data(150, '3')
    print(f"   Part 1: +{len(low_band_p1)}")
    print(f"   Part 2: +{len(low_band_p2)}")
    print(f"   Part 3: +{len(low_band_p3)}")
    
    # Объединяем все
    all_answers = to_keep + regenerated + low_band_p1 + low_band_p2 + low_band_p3
    
    # Сортируем по answer_id
    try:
        all_answers.sort(key=lambda x: int(x['answer_id'].split('_')[1]))
    except:
        pass
    
    # Создаем v1.3
    output_dir = 'dataset_versions/v1.3'
    os.makedirs(output_dir, exist_ok=True)
    
    # Копируем users и sessions
    for file in ['users.csv', 'sessions.csv']:
        src = f'dataset_versions/v1.2/{file}'
        dst = f'{output_dir}/{file}'
        if os.path.exists(src):
            shutil.copy2(src, dst)
    
    # Сохраняем answers
    output_file = f'{output_dir}/answers.csv'
    print(f"\n💾 Сохранение в {output_file}...")
    
    fieldnames = ['answer_id', 'session_id', 'user_id', 'part', 'question_id', 'question_text',
                 'answer_text', 'duration_sec', 'target_band_overall', 'target_band_fc',
                 'target_band_lr', 'target_band_gra', 'target_band_pr', 'transcript_raw',
                 'source_type', 'quality_flag']
    
    # Очищаем от None
    cleaned_answers = []
    for answer in all_answers:
        cleaned = {k: (answer.get(k) or '') for k in fieldnames}
        cleaned_answers.append(cleaned)
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_answers)
    
    # Статистика
    print("\n" + "=" * 70)
    print("✅ СТАТИСТИКА V1.3")
    print("=" * 70)
    print(f"   Всего ответов: {len(cleaned_answers)}")
    
    part_counts = defaultdict(int)
    for a in cleaned_answers:
        part_counts[a['part']] += 1
    
    for part in sorted(part_counts.keys()):
        count = part_counts[part]
        pct = count / len(cleaned_answers) * 100
        print(f"   Part {part}: {count} ({pct:.1f}%)")
    
    # Распределение по бэндам
    overall_scores = []
    for a in cleaned_answers:
        try:
            overall_scores.append(float(a.get('target_band_overall', 0)))
        except:
            pass
    
    low_mid = sum(1 for s in overall_scores if s <= 6.0)
    high = sum(1 for s in overall_scores if s >= 6.5)
    
    print(f"\n   Low-Mid (≤6.0): {low_mid} ({low_mid/len(overall_scores)*100:.1f}%)")
    print(f"   High (≥6.5): {high} ({high/len(overall_scores)*100:.1f}%)")
    
    # Сохраняем changelog
    changelog = f"""# V1.3 Changelog

## Изменения от v1.2

### Удалено
- {len(to_delete)} проблемных ответов

### Регенерировано
- Part 1: {sum(1 for a in to_regenerate if a.get('part') == '1')} ответов
- Part 2: {sum(1 for a in to_regenerate if a.get('part') == '2')} ответов
- Part 3: {sum(1 for a in to_regenerate if a.get('part') == '3')} ответов

### Добавлено
- Part 1: +{len(low_band_p1)} low-band ответов (4.0-5.0)
- Part 2: +{len(low_band_p2)} low-band ответов
- Part 3: +{len(low_band_p3)} low-band ответов

### Итого
- Всего ответов: {len(cleaned_answers)}
- Part 1: {part_counts.get('1', 0)}
- Part 2: {part_counts.get('2', 0)}
- Part 3: {part_counts.get('3', 0)}

## Улучшения

1. Убраны мусорные формулировки Part 1 ("genuine appreciation", etc.)
2. Исправлены шаблонные ошибки Part 2 ("time when you", etc.)
3. Очищены академические фразы Part 3
4. Добавлены low-band ответы для баланса
5. Проверена релевантность ответов вопросам
"""
    
    with open(f'{output_dir}/CHANGELOG.md', 'w', encoding='utf-8') as f:
        f.write(changelog)
    
    print(f"\n💾 Changelog сохранен в {output_dir}/CHANGELOG.md")
    print(f"\n✅ V1.3 создан в {output_dir}/")

if __name__ == '__main__':
    main()

