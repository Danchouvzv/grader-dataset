#!/usr/bin/env python3
"""
Регенерация Part 3 с использованием улучшенной v2 генерации

Фильтрует старые шаблонные ответы и заменяет их на новые с:
- Тематическими словарями
- Множественными структурными шаблонами
- Четкими различиями между бэндами
"""

import csv
import random
import os
from generate_part3_expansion_v2 import generate_part3_answer_v2, generate_part3_questions
from generate_synthetic_expansion import generate_realistic_subbands
from improve_generation import determine_quality_flag

# Шаблоны для фильтрации (старые, которые нужно заменить)
OLD_TEMPLATE_PREFIXES = [
    "This represents one of the most pressing and complex challenges of our time",
    "This is a multifaceted issue that requires careful consideration of various factors",
    "I think this is a complex issue that has multiple aspects",
    "I think this is complex question",
    "This is a multifaceted issue",
    "This represents one of the most pressing",
    "I think this is a complex issue",
]

# Также фильтруем по ключевым фразам внутри текста
OLD_TEMPLATE_PHRASES = [
    "navigate multiple competing priorities",
    "maximize benefits while minimizing harm",
    "balanced approach that maximizes benefits",
    "requires careful consideration of various factors",
]

def is_old_template(answer_text: str) -> bool:
    """Проверяет, является ли ответ старым шаблоном"""
    answer_lower = answer_text.lower().strip()
    
    # Проверка по префиксам
    for prefix in OLD_TEMPLATE_PREFIXES:
        if answer_lower.startswith(prefix.lower()):
            return True
    
    # Проверка по ключевым фразам (если есть 2+ из списка - вероятно старый шаблон)
    phrase_count = sum(1 for phrase in OLD_TEMPLATE_PHRASES if phrase.lower() in answer_lower)
    if phrase_count >= 2:
        return True
    
    return False

def load_answers(filepath: str):
    """Загружает ответы из CSV"""
    answers = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            answers.append(row)
    return answers

def main():
    print("=" * 70)
    print("РЕГЕНЕРАЦИЯ PART 3 С УЛУЧШЕННОЙ V2 ГЕНЕРАЦИЕЙ")
    print("=" * 70)
    
    # Загружаем v1.1
    input_file = 'dataset_versions/v1.1/answers.csv'
    print(f"\n📂 Загрузка {input_file}...")
    answers = load_answers(input_file)
    print(f"   Загружено: {len(answers)} ответов")
    
    # Фильтруем Part 3
    part3_answers = [a for a in answers if a['part'] == '3']
    print(f"\n📊 Part 3 ответов: {len(part3_answers)}")
    
    # Находим старые шаблоны
    old_templates = []
    new_answers = []
    
    for answer in answers:
        if answer['part'] == '3' and is_old_template(answer.get('answer_text', '')):
            old_templates.append(answer)
        else:
            new_answers.append(answer)
    
    print(f"   Старых шаблонных ответов: {len(old_templates)}")
    print(f"   Ответов для сохранения: {len(new_answers)}")
    
    # Загружаем вопросы
    questions = generate_part3_questions()
    question_dict = {q[0]: q[1] for q in questions}
    
    # Получаем user_ids и session_ids из существующих ответов
    user_ids = list(set(a['user_id'] for a in answers))
    session_ids = list(set(a['session_id'] for a in answers))
    
    # Регенерируем Part 3 ответы
    print(f"\n🔄 Регенерация {len(old_templates)} Part 3 ответов через v2...")
    
    random.seed(42)
    regenerated = []
    
    for old_answer in old_templates:
        try:
            overall = float(old_answer['target_band_overall'])
            fc = float(old_answer['target_band_fc'])
            lr = float(old_answer['target_band_lr'])
            gra = float(old_answer['target_band_gra'])
            pr = float(old_answer['target_band_pr'])
            
            question_text = old_answer.get('question_text', '')
            if not question_text:
                # Пытаемся найти вопрос по question_id
                q_id = old_answer.get('question_id', '')
                question_text = question_dict.get(q_id, 'How important is education in modern society?')
            
            # Генерируем новый ответ через v2
            answer_text, duration = generate_part3_answer_v2(
                question_text, overall, fc, lr, gra, pr
            )
            
            # Создаем новый ответ (сохраняем все поля, кроме текста)
            new_answer = old_answer.copy()
            new_answer['answer_text'] = answer_text
            new_answer['transcript_raw'] = answer_text
            new_answer['duration_sec'] = str(duration)
            new_answer['source_type'] = 'synthetic_v1.2'
            new_answer['quality_flag'] = determine_quality_flag(overall)
            
            regenerated.append(new_answer)
            
        except Exception as e:
            print(f"   ⚠️  Ошибка при регенерации {old_answer.get('answer_id', 'unknown')}: {e}")
            # Оставляем старый ответ, если не удалось регенерировать
            new_answers.append(old_answer)
    
    print(f"   ✅ Регенерировано: {len(regenerated)} ответов")
    
    # Объединяем все ответы
    all_answers = new_answers + regenerated
    
    # Сортируем по answer_id для консистентности
    try:
        all_answers.sort(key=lambda x: int(x['answer_id'].split('_')[1]))
    except:
        pass
    
    # Сохраняем в v1.2
    output_dir = 'dataset_versions/v1.2'
    os.makedirs(output_dir, exist_ok=True)
    
    # Копируем users и sessions из v1.1
    import shutil
    for file in ['users.csv', 'sessions.csv']:
        src = f'dataset_versions/v1.1/{file}'
        dst = f'{output_dir}/{file}'
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"   📋 Скопирован {file}")
    
    # Сохраняем обновленные answers
    output_file = f'{output_dir}/answers.csv'
    print(f"\n💾 Сохранение в {output_file}...")
    
    # Очищаем словари от None и лишних полей
    fieldnames = ['answer_id', 'session_id', 'user_id', 'part', 'question_id', 'question_text',
                 'answer_text', 'duration_sec', 'target_band_overall', 'target_band_fc',
                 'target_band_lr', 'target_band_gra', 'target_band_pr', 'transcript_raw',
                 'source_type', 'quality_flag']
    
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
    print("✅ СТАТИСТИКА V1.2")
    print("=" * 70)
    print(f"   Всего ответов: {len(all_answers)}")
    
    part_counts = {}
    for a in all_answers:
        part = a['part']
        part_counts[part] = part_counts.get(part, 0) + 1
    
    for part in sorted(part_counts.keys()):
        print(f"   Part {part}: {part_counts[part]} ответов")
    
    # Проверка на старые шаблоны
    old_count = sum(1 for a in all_answers if a['part'] == '3' and is_old_template(a.get('answer_text', '')))
    print(f"\n   Старых шаблонов в Part 3: {old_count} (было {len(old_templates)})")
    
    if old_count == 0:
        print("   ✅ Все старые шаблоны заменены!")
    else:
        print(f"   ⚠️  Осталось {old_count} старых шаблонов")
    
    print(f"\n✅ V1.2 создан в {output_dir}/")

if __name__ == '__main__':
    main()

