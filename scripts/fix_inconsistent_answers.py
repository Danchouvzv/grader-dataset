#!/usr/bin/env python3
"""
Обработка inconsistent ответов для v1.3
- Weighted training: помечает inconsistent для снижения веса
- Авто-правка: downgrade/upgrade по правилам
- Удаление самого трэша
"""

import csv
import re
from collections import defaultdict

def count_complex_structures(text: str) -> int:
    """Считает сложные грамматические структуры"""
    count = 0
    if re.search(r'\b(who|which|that|where|when)\s+\w+', text, re.I):
        count += 1
    if re.search(r'\bhad\s+\w+ed\b', text, re.I):
        count += 1
    if re.search(r'\b(if|unless|provided)\s+', text, re.I):
        count += 1
    if re.search(r'\b(however|moreover|furthermore|nevertheless|consequently)\b', text, re.I):
        count += 1
    return count

def count_advanced_vocab(text: str) -> int:
    """Считает продвинутую лексику"""
    advanced_words = [
        'significant', 'considerable', 'substantial', 'profound', 'fundamental',
        'comprehensive', 'sophisticated', 'nuanced', 'intricate', 'complex',
        'appreciate', 'value', 'acknowledge', 'recognize', 'perceive',
        'challenge', 'opportunity', 'perspective', 'approach', 'strategy'
    ]
    text_lower = text.lower()
    return sum(1 for word in advanced_words if word in text_lower)

def count_errors(text: str) -> int:
    """Считает грамматические ошибки"""
    count = 0
    if re.search(r'\b(he|she|it|they)\s+(go|do|make|have|be)\b', text, re.I):
        count += 1
    if re.search(r'\b(yesterday|last\s+week)\s+\w+\s+(is|are|am)\b', text, re.I):
        count += 1
    words = text.lower().split()
    for i in range(len(words) - 1):
        if words[i] == words[i+1] and len(words[i]) > 3:
            count += 1
    return count

def has_thematic_words(text: str, question: str) -> bool:
    """Проверяет наличие тематических слов из вопроса"""
    question_words = set(re.findall(r'\b\w+\b', question.lower()))
    answer_words = set(re.findall(r'\b\w+\b', text.lower()))
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'do', 'does', 'did',
                 'have', 'has', 'had', 'will', 'would', 'could', 'should', 'what',
                 'when', 'where', 'which', 'who', 'how', 'why', 'this', 'that'}
    question_words = {w for w in question_words if len(w) > 3 and w not in stopwords}
    answer_words = {w for w in answer_words if len(w) > 3 and w not in stopwords}
    return len(question_words.intersection(answer_words)) >= 1

def fix_inconsistent(answer: dict, consistency_result: dict) -> dict:
    """Исправляет inconsistent ответ по правилам"""
    text = answer.get('answer_text', '')
    question = answer.get('question_text', '')
    
    try:
        overall = float(answer.get('target_band_overall', 0))
    except:
        return answer
    
    word_count = len(text.split())
    complex_structures = count_complex_structures(text)
    advanced_vocab = count_advanced_vocab(text)
    errors = count_errors(text)
    
    fixed = answer.copy()
    action = 'keep'
    new_overall = overall
    sample_weight = 1.0
    quality_flag = answer.get('quality_flag', 'ok')
    
    # High band (7.0+) но короткий текст
    if overall >= 7.0:
        if word_count < 30:
            # Вариант 1: Downgrade
            if not has_thematic_words(text, question):
                action = 'downgrade'
                new_overall = 6.0
                quality_flag = 'inconsistent_downgraded'
            # Вариант 2: Weighted
            else:
                action = 'weighted'
                sample_weight = 0.4
                quality_flag = 'inconsistent_weighted'
        
        if complex_structures == 0 and overall >= 7.5:
            action = 'weighted'
            sample_weight = min(sample_weight, 0.5)
            quality_flag = 'inconsistent_weighted'
        
        if advanced_vocab < 2 and overall >= 7.5:
            action = 'weighted'
            sample_weight = min(sample_weight, 0.5)
            quality_flag = 'inconsistent_weighted'
        
        if errors > 2:
            action = 'weighted'
            sample_weight = min(sample_weight, 0.6)
            quality_flag = 'inconsistent_weighted'
    
    # Low band (≤5.0) но слишком чистый текст
    if overall <= 5.0:
        if complex_structures > 2:
            action = 'upgrade'
            new_overall = min(6.0, overall + 1.0)
            quality_flag = 'inconsistent_upgraded'
        
        if advanced_vocab > 3:
            action = 'upgrade'
            new_overall = min(6.0, overall + 0.5)
            quality_flag = 'inconsistent_upgraded'
        
        if errors == 0 and overall <= 4.5:
            # Регенерировать или upgrade
            action = 'upgrade'
            new_overall = 5.0
            quality_flag = 'inconsistent_upgraded'
    
    # Жёсткий фильтр: high_band & short & no_thematic_words
    if overall >= 7.0 and word_count < 25 and not has_thematic_words(text, question):
        action = 'remove'
        quality_flag = 'inconsistent_removed'
    
    # Обновляем ответ
    if action == 'downgrade' or action == 'upgrade':
        fixed['target_band_overall'] = str(new_overall)
        # Пересчитываем субскоры
        fc = float(fixed.get('target_band_fc', new_overall))
        lr = float(fixed.get('target_band_lr', new_overall))
        gra = float(fixed.get('target_band_gra', new_overall))
        pr = float(fixed.get('target_band_pr', new_overall))
        
        # Корректируем субскоры под новый overall
        diff = new_overall - overall
        fixed['target_band_fc'] = str(max(3.0, min(9.0, fc + diff * 0.8)))
        fixed['target_band_lr'] = str(max(3.0, min(9.0, lr + diff * 0.8)))
        fixed['target_band_gra'] = str(max(3.0, min(9.0, gra + diff * 0.8)))
        fixed['target_band_pr'] = str(max(3.0, min(9.0, pr + diff * 0.8)))
    
    fixed['quality_flag'] = quality_flag
    fixed['sample_weight'] = str(sample_weight)
    fixed['is_inconsistent'] = 'true' if action != 'keep' else 'false'
    
    return (fixed, action)

def main():
    print("=" * 70)
    print("ОБРАБОТКА INCONSISTENT ОТВЕТОВ")
    print("=" * 70)
    
    # Загружаем v1.3
    answers = []
    with open('dataset_versions/v1.3/answers.csv', 'r', encoding='utf-8') as f:
        answers = list(csv.DictReader(f))
    
    print(f"\n📂 Загружено: {len(answers)} ответов")
    
    # Загружаем результаты consistency check
    consistency_results = {}
    with open('docs/consistency_check_v1.3.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            consistency_results[row['answer_id']] = row
    
    print(f"📋 Загружено: {len(consistency_results)} результатов consistency check")
    
    # Обрабатываем inconsistent
    fixed_answers = []
    removed_answers = []
    actions = defaultdict(int)
    
    for answer in answers:
        answer_id = answer.get('answer_id')
        if answer_id not in consistency_results:
            # Не было в consistency check - оставляем как есть
            answer['sample_weight'] = '1.0'
            answer['is_inconsistent'] = 'false'
            fixed_answers.append(answer)
            continue
        
        consistency = consistency_results[answer_id]
        if consistency.get('action') == 'ok':
            # Consistent - оставляем как есть
            answer['sample_weight'] = '1.0'
            answer['is_inconsistent'] = 'false'
            fixed_answers.append(answer)
        else:
            # Inconsistent - исправляем
            result = fix_inconsistent(answer, consistency)
            if isinstance(result, tuple):
                fixed, action = result
            else:
                fixed = result
                action = 'keep'
            actions[action] += 1
            
            if action == 'remove':
                removed_answers.append(fixed)
            else:
                fixed_answers.append(fixed)
    
    print(f"\n📊 РЕЗУЛЬТАТЫ ОБРАБОТКИ:")
    print(f"   ✅ Keep: {actions['keep']}")
    print(f"   ⬇️  Downgrade: {actions['downgrade']}")
    print(f"   ⬆️  Upgrade: {actions['upgrade']}")
    print(f"   ⚖️  Weighted: {actions['weighted']}")
    print(f"   🗑️  Remove: {actions['remove']}")
    
    # Сохраняем исправленный датасет
    output_file = 'dataset_versions/v1.3/answers_fixed.csv'
    fieldnames = ['answer_id', 'session_id', 'user_id', 'part', 'question_id', 'question_text',
                 'answer_text', 'duration_sec', 'target_band_overall', 'target_band_fc',
                 'target_band_lr', 'target_band_gra', 'target_band_pr', 'transcript_raw',
                 'source_type', 'quality_flag', 'sample_weight', 'is_inconsistent']
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for answer in fixed_answers:
            row = {k: answer.get(k, '') for k in fieldnames}
            writer.writerow(row)
    
    print(f"\n💾 Исправленный датасет сохранен в {output_file}")
    
    # Сохраняем удаленные
    if removed_answers:
        removed_file = 'dataset_versions/v1.3/removed_inconsistent.csv'
        with open(removed_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for answer in removed_answers:
                row = {k: answer.get(k, '') for k in fieldnames}
                writer.writerow(row)
        print(f"💾 Удаленные ответы сохранены в {removed_file}")
    
    # Статистика по весам
    weights = defaultdict(int)
    for answer in fixed_answers:
        weight = float(answer.get('sample_weight', 1.0))
        weight_key = f"{weight:.1f}"
        weights[weight_key] += 1
    
    print(f"\n📊 РАСПРЕДЕЛЕНИЕ ПО ВЕСАМ:")
    for weight in sorted(weights.keys(), reverse=True):
        print(f"   Weight {weight}: {weights[weight]} ответов")
    
    print(f"\n✅ Обработка завершена")
    print(f"   Всего ответов: {len(fixed_answers)}")
    print(f"   Удалено: {len(removed_answers)}")

if __name__ == '__main__':
    main()

