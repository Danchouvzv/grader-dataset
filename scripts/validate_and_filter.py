#!/usr/bin/env python3
"""
Валидация и фильтрация ответов для v1.3
Проверяет Part 1, 2, 3 на проблемы и помечает для регенерации/удаления
"""

import csv
import re
from collections import defaultdict

# Запрещенные фразы для Part 1
PART1_FORBIDDEN = [
    "genuine appreciation",
    "deeply engaged",
    "fundamental aspect",
    "intellectual enrichment",
    "personal fulfillment",
]

# Запрещенные фразы для Part 2
PART2_FORBIDDEN = [
    "I'd like to describe time when you",
    "This was something that happened about a year ago",
    "What made it particularly memorable",
    "challenged my expectations",
    "opened up new perspectives",
]

# Запрещенные фразы для Part 3
PART3_FORBIDDEN = [
    "represents one of the most pressing and complex challenges",
    "fundamental tension in contemporary society",
    "navigate change in complex systems",
    "adaptive frameworks that can evolve",
    "incorporating diverse stakeholders",
]

def count_words(text: str) -> int:
    return len(text.split())

def check_question_relevance(answer: str, question: str) -> bool:
    """Проверяет, содержит ли ответ слова из вопроса"""
    if not answer or not question:
        return False
    
    question_words = set(re.findall(r'\b\w+\b', question.lower()))
    answer_words = set(re.findall(r'\b\w+\b', answer.lower()))
    
    # Исключаем служебные слова
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'do', 'does', 'did', 
                 'have', 'has', 'had', 'will', 'would', 'could', 'should', 'what', 
                 'when', 'where', 'which', 'who', 'how', 'why', 'this', 'that', 'these', 'those'}
    
    question_words = {w for w in question_words if len(w) > 3 and w not in stopwords}
    answer_words = {w for w in answer_words if len(w) > 3 and w not in stopwords}
    
    # Должно быть хотя бы 1-2 общих слова
    common = question_words.intersection(answer_words)
    return len(common) >= 1

def validate_part1(answer: dict) -> dict:
    """Валидирует Part 1 ответ"""
    text = answer.get('answer_text', '')
    question = answer.get('question_text', '')
    try:
        overall = float(answer.get('target_band_overall', 0))
    except (ValueError, TypeError):
        return {
            'answer_id': answer.get('answer_id'),
            'part': answer.get('part'),
            'overall': 0,
            'issues': ['Invalid overall score'],
            'action': 'delete'
        }
    
    issues = []
    action = 'keep'
    
    # Проверка длины
    word_count = count_words(text)
    if word_count < 10:
        issues.append(f"Too short ({word_count} words)")
        action = 'regenerate'
    elif word_count > 50:
        issues.append(f"Too long ({word_count} words)")
        action = 'regenerate'
    
    # Проверка запрещенных фраз
    text_lower = text.lower()
    for phrase in PART1_FORBIDDEN:
        if phrase.lower() in text_lower:
            issues.append(f"Forbidden phrase: {phrase}")
            action = 'regenerate'
    
    # Проверка релевантности
    if not check_question_relevance(text, question):
        issues.append("No words from question in answer")
        action = 'regenerate'
    
    # Проверка consistency (overall vs текст)
    if overall >= 7.0:
        if word_count < 20 or not any(word in text_lower for word in ['enjoy', 'like', 'appreciate', 'value', 'interested']):
            issues.append("High band but simple text")
            action = 'regenerate'
    
    if overall <= 5.0:
        if 'genuine' in text_lower or 'fundamental' in text_lower or 'intellectual' in text_lower:
            issues.append("Low band but academic phrases")
            action = 'regenerate'
    
    return {
        'answer_id': answer.get('answer_id'),
        'part': answer.get('part'),
        'overall': overall,
        'issues': issues,
        'action': action
    }

def validate_part2(answer: dict) -> dict:
    """Валидирует Part 2 ответ"""
    text = answer.get('answer_text', '')
    question = answer.get('question_text', '')
    try:
        overall = float(answer.get('target_band_overall', 0))
    except (ValueError, TypeError):
        return {
            'answer_id': answer.get('answer_id'),
            'part': answer.get('part'),
            'overall': 0,
            'issues': ['Invalid overall score'],
            'action': 'delete'
        }
    
    issues = []
    action = 'keep'
    
    # Проверка длины (Part 2 должен быть длинным!)
    word_count = count_words(text)
    if word_count < 50:
        issues.append(f"Too short for Part 2 ({word_count} words, should be 100-180)")
        action = 'regenerate'
    elif word_count > 200:
        issues.append(f"Too long ({word_count} words)")
        action = 'regenerate'
    
    # Проверка запрещенных фраз
    text_lower = text.lower()
    for phrase in PART2_FORBIDDEN:
        if phrase.lower() in text_lower:
            issues.append(f"Forbidden phrase: {phrase}")
            action = 'regenerate'
    
    # Проверка на "time when you" ошибку
    if "time when you" in text_lower or "describe time" in text_lower:
        issues.append("Template error: 'time when you'")
        action = 'regenerate'
    
    # Проверка consistency
    if overall >= 7.0 and word_count < 100:
        issues.append("High band but too short")
        action = 'regenerate'
    
    return {
        'answer_id': answer.get('answer_id'),
        'part': answer.get('part'),
        'overall': overall,
        'issues': issues,
        'action': action
    }

def validate_part3(answer: dict) -> dict:
    """Валидирует Part 3 ответ"""
    text = answer.get('answer_text', '')
    try:
        overall = float(answer.get('target_band_overall', 0))
    except (ValueError, TypeError):
        return {
            'answer_id': answer.get('answer_id'),
            'part': answer.get('part'),
            'overall': 0,
            'issues': ['Invalid overall score'],
            'action': 'delete'
        }
    
    issues = []
    action = 'keep'
    
    # Проверка длины
    word_count = count_words(text)
    if word_count < 20:
        issues.append(f"Too short ({word_count} words)")
        action = 'delete'
    elif word_count > 80:
        issues.append(f"Too long ({word_count} words, looks like essay)")
        action = 'regenerate'
    
    # Проверка запрещенных фраз
    text_lower = text.lower()
    for phrase in PART3_FORBIDDEN:
        if phrase.lower() in text_lower:
            issues.append(f"Forbidden phrase: {phrase}")
            action = 'regenerate'
    
    # Проверка сложных предложений
    sentences = re.split(r'[.!?]+', text)
    complex_count = sum(1 for s in sentences if s.count(',') >= 3)
    if complex_count > 2:
        issues.append(f"Too many complex sentences ({complex_count})")
        action = 'regenerate'
    
    return {
        'answer_id': answer.get('answer_id'),
        'part': answer.get('part'),
        'overall': overall,
        'issues': issues,
        'action': action
    }

def main():
    print("=" * 70)
    print("ВАЛИДАЦИЯ И ФИЛЬТРАЦИЯ ДЛЯ V1.3")
    print("=" * 70)
    
    filepath = 'dataset_versions/v1.2/answers.csv'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        answers = list(csv.DictReader(f))
    
    print(f"\n📂 Загружено: {len(answers)} ответов")
    
    # Валидируем все
    results = []
    for answer in answers:
        part = answer.get('part', '')
        if part == '1':
            result = validate_part1(answer)
        elif part == '2':
            result = validate_part2(answer)
        elif part == '3':
            result = validate_part3(answer)
        else:
            continue
        
        results.append(result)
    
    # Статистика
    actions = defaultdict(int)
    for r in results:
        actions[r['action']] += 1
    
    print(f"\n📊 РЕЗУЛЬТАТЫ ВАЛИДАЦИИ:")
    print(f"   ✅ Keep: {actions['keep']} ({actions['keep']/len(results)*100:.1f}%)")
    print(f"   🔄 Regenerate: {actions['regenerate']} ({actions['regenerate']/len(results)*100:.1f}%)")
    print(f"   🗑️  Delete: {actions['delete']} ({actions['delete']/len(results)*100:.1f}%)")
    
    # По частям
    print(f"\n📋 ПО ЧАСТЯМ:")
    for part in ['1', '2', '3']:
        part_results = [r for r in results if r.get('part') == part]
        part_actions = defaultdict(int)
        for r in part_results:
            part_actions[r['action']] += 1
        print(f"   Part {part}: keep={part_actions['keep']}, regenerate={part_actions['regenerate']}, delete={part_actions['delete']}")
    
    # Сохраняем результаты
    output_file = 'docs/validation_results_v1.3.csv'
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['answer_id', 'part', 'overall', 'action', 'issues']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({
                'answer_id': result['answer_id'],
                'part': result['part'],
                'overall': result['overall'],
                'action': result['action'],
                'issues': '; '.join(result['issues'])
            })
    
    print(f"\n💾 Результаты сохранены в {output_file}")
    print(f"\n✅ Валидация завершена")

if __name__ == '__main__':
    main()

