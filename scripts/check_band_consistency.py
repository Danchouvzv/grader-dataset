#!/usr/bin/env python3
"""
Проверка consistency бэндов
Находит ответы, где overall не соответствует тексту
"""

import csv
import re
from collections import defaultdict

def count_complex_structures(text: str) -> int:
    """Считает сложные грамматические структуры"""
    count = 0
    # Relative clauses
    if re.search(r'\b(who|which|that|where|when)\s+\w+', text, re.I):
        count += 1
    # Past perfect
    if re.search(r'\bhad\s+\w+ed\b', text, re.I):
        count += 1
    # Conditionals
    if re.search(r'\b(if|unless|provided)\s+', text, re.I):
        count += 1
    # Complex linking
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
    count = sum(1 for word in advanced_words if word in text_lower)
    return count

def count_errors(text: str) -> int:
    """Считает грамматические ошибки"""
    count = 0
    # Пропуск артиклей
    if re.search(r'\b(he|she|it|they)\s+(go|do|make|have|be)\b', text, re.I):
        count += 1
    # Неправильные времена
    if re.search(r'\b(yesterday|last\s+week)\s+\w+\s+(is|are|am)\b', text, re.I):
        count += 1
    # Повторы слов
    words = text.lower().split()
    for i in range(len(words) - 1):
        if words[i] == words[i+1] and len(words[i]) > 3:
            count += 1
    return count

def check_consistency(answer: dict) -> dict:
    """Проверяет consistency бэнда и текста"""
    text = answer.get('answer_text', '')
    try:
        overall = float(answer.get('target_band_overall', 0))
    except:
        return {
            'answer_id': answer.get('answer_id'),
            'part': answer.get('part'),
            'overall': 0,
            'issue': 'Invalid score',
            'action': 'delete'
        }
    
    word_count = len(text.split())
    complex_structures = count_complex_structures(text)
    advanced_vocab = count_advanced_vocab(text)
    errors = count_errors(text)
    
    issues = []
    action = 'ok'
    
    # High band (≥7.0) но простой текст
    if overall >= 7.0:
        if word_count < 30:
            issues.append(f"High band but short ({word_count} words)")
            action = 'regenerate'
        if complex_structures == 0 and overall >= 7.5:
            issues.append("High band but no complex structures")
            action = 'regenerate'
        if advanced_vocab < 2 and overall >= 7.5:
            issues.append("High band but limited vocabulary")
            action = 'regenerate'
        if errors > 2:
            issues.append(f"High band but many errors ({errors})")
            action = 'regenerate'
    
    # Low band (≤5.0) но слишком чистый текст
    if overall <= 5.0:
        if complex_structures > 2:
            issues.append(f"Low band but complex structures ({complex_structures})")
            action = 'regenerate'
        if advanced_vocab > 3:
            issues.append(f"Low band but advanced vocab ({advanced_vocab})")
            action = 'regenerate'
        if errors == 0 and overall <= 4.5:
            issues.append("Low band but no errors")
            action = 'regenerate'
    
    return {
        'answer_id': answer.get('answer_id'),
        'part': answer.get('part'),
        'overall': overall,
        'word_count': word_count,
        'complex_structures': complex_structures,
        'advanced_vocab': advanced_vocab,
        'errors': errors,
        'issues': issues,
        'action': action
    }

def main():
    print("=" * 70)
    print("ПРОВЕРКА CONSISTENCY БЭНДОВ")
    print("=" * 70)
    
    filepath = 'dataset_versions/v1.3/answers.csv'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        answers = list(csv.DictReader(f))
    
    print(f"\n📂 Загружено: {len(answers)} ответов")
    
    # Проверяем все
    results = []
    for answer in answers:
        result = check_consistency(answer)
        results.append(result)
    
    # Статистика
    actions = defaultdict(int)
    for r in results:
        actions[r['action']] += 1
    
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"   ✅ OK: {actions['ok']} ({actions['ok']/len(results)*100:.1f}%)")
    print(f"   🔄 Regenerate: {actions['regenerate']} ({actions['regenerate']/len(results)*100:.1f}%)")
    print(f"   🗑️  Delete: {actions['delete']} ({actions['delete']/len(results)*100:.1f}%)")
    
    # Примеры проблемных
    problematic = [r for r in results if r['action'] != 'ok']
    print(f"\n🔴 ПРОБЛЕМНЫХ: {len(problematic)}")
    
    if problematic:
        print("\n   Примеры:")
        for r in problematic[:5]:
            print(f"   - {r['answer_id']} (Part {r['part']}, Overall {r['overall']}): {', '.join(r['issues'])}")
    
    # Сохраняем результаты
    output_file = 'docs/consistency_check_v1.3.csv'
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['answer_id', 'part', 'overall', 'word_count', 'complex_structures',
                     'advanced_vocab', 'errors', 'action', 'issues']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({
                'answer_id': result['answer_id'],
                'part': result['part'],
                'overall': result['overall'],
                'word_count': result['word_count'],
                'complex_structures': result['complex_structures'],
                'advanced_vocab': result['advanced_vocab'],
                'errors': result['errors'],
                'action': result['action'],
                'issues': '; '.join(result['issues'])
            })
    
    print(f"\n💾 Результаты сохранены в {output_file}")
    print(f"\n✅ Проверка завершена")

if __name__ == '__main__':
    main()

