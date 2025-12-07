#!/usr/bin/env python3
"""
Пост-валидатор для Part 3
Фильтрует подозрительные ответы (слишком академические, слишком длинные, etc.)
"""

import csv
import re

# Запрещенные академические фразы
ACADEMIC_RED_FLAGS = [
    "represents a complex challenge with multiple dimensions",
    "fundamental tension in contemporary society",
    "navigate change in complex systems",
    "pressing and complex challenges of our time",
    "adaptive frameworks that can evolve",
    "incorporating diverse stakeholders",
    "competing priorities and perspectives",
    "nuanced solutions that can adapt",
    "thoughtful, evidence-based approaches",
    "sophisticated understanding of",
    "empirical evidence",
    "systematic approaches",
    "comprehensive frameworks",
]

def count_words(text: str) -> int:
    """Считает количество слов"""
    return len(text.split())

def count_complex_sentences(text: str) -> int:
    """Считает сложные предложения (с множеством запятых)"""
    sentences = re.split(r'[.!?]+', text)
    complex_count = 0
    for sent in sentences:
        if sent.count(',') >= 3:  # 3+ запятых = сложное предложение
            complex_count += 1
    return complex_count

def check_academic_phrases(text: str) -> list:
    """Проверяет наличие академических фраз"""
    text_lower = text.lower()
    found = []
    for phrase in ACADEMIC_RED_FLAGS:
        if phrase.lower() in text_lower:
            found.append(phrase)
    return found

def validate_answer(answer: dict) -> dict:
    """Валидирует один ответ"""
    text = answer.get('answer_text', '')
    word_count = count_words(text)
    complex_sentences = count_complex_sentences(text)
    academic_phrases = check_academic_phrases(text)
    
    issues = []
    severity = 'ok'
    
    # Проверка длины
    if word_count < 20:
        issues.append(f"Too short ({word_count} words)")
        severity = 'suspicious'
    elif word_count > 80:
        issues.append(f"Too long ({word_count} words, looks like essay)")
        severity = 'suspicious'
    
    # Проверка академических фраз
    if academic_phrases:
        issues.append(f"Academic phrases found: {', '.join(academic_phrases[:2])}")
        severity = 'suspicious'
    
    # Проверка сложных предложений
    if complex_sentences > 2:
        issues.append(f"Too many complex sentences ({complex_sentences})")
        severity = 'suspicious'
    
    return {
        'answer_id': answer.get('answer_id'),
        'overall': answer.get('target_band_overall'),
        'word_count': word_count,
        'complex_sentences': complex_sentences,
        'academic_phrases': len(academic_phrases),
        'issues': issues,
        'severity': severity
    }

def main():
    print("=" * 70)
    print("ПОСТ-ВАЛИДАЦИЯ PART 3")
    print("=" * 70)
    
    filepath = 'dataset_versions/v1.2/answers.csv'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        answers = list(csv.DictReader(f))
    
    # Фильтруем Part 3
    part3 = [a for a in answers if a['part'] == '3']
    print(f"\n📊 Part 3 ответов: {len(part3)}")
    
    # Валидируем все
    print("\n🔍 Валидация...")
    results = []
    for answer in part3:
        result = validate_answer(answer)
        results.append(result)
    
    # Статистика
    suspicious = [r for r in results if r['severity'] == 'suspicious']
    ok_count = len(results) - len(suspicious)
    
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"   ✅ OK: {ok_count} ({ok_count/len(results)*100:.1f}%)")
    print(f"   ⚠️  Suspicious: {len(suspicious)} ({len(suspicious)/len(results)*100:.1f}%)")
    
    # Детали по проблемам
    print("\n📋 ДЕТАЛИ ПРОБЛЕМ:")
    
    too_long = sum(1 for r in suspicious if 'Too long' in str(r['issues']))
    too_short = sum(1 for r in suspicious if 'Too short' in str(r['issues']))
    academic = sum(1 for r in suspicious if r['academic_phrases'] > 0)
    complex_sent = sum(1 for r in suspicious if 'complex sentences' in str(r['issues']))
    
    print(f"   Слишком длинных (>80 слов): {too_long}")
    print(f"   Слишком коротких (<20 слов): {too_short}")
    print(f"   С академическими фразами: {academic}")
    print(f"   Слишком сложных предложений: {complex_sent}")
    
    # Примеры проблемных
    print("\n🔴 ПРИМЕРЫ ПОДОЗРИТЕЛЬНЫХ ОТВЕТОВ:")
    for i, result in enumerate(suspicious[:5], 1):
        print(f"\n   {i}. Answer ID: {result['answer_id']}")
        print(f"      Overall: {result['overall']}")
        print(f"      Проблемы: {', '.join(result['issues'])}")
        
        # Находим полный ответ
        answer = next((a for a in part3 if a['answer_id'] == result['answer_id']), None)
        if answer:
            print(f"      Текст: {answer.get('answer_text', '')[:100]}...")
    
    # Сохраняем результаты
    output_file = 'docs/post_validation_part3.csv'
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['answer_id', 'overall', 'word_count', 'complex_sentences', 
                     'academic_phrases', 'severity', 'issues']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                'answer_id': result['answer_id'],
                'overall': result['overall'],
                'word_count': result['word_count'],
                'complex_sentences': result['complex_sentences'],
                'academic_phrases': result['academic_phrases'],
                'severity': result['severity'],
                'issues': '; '.join(result['issues'])
            })
    
    print(f"\n💾 Результаты сохранены в {output_file}")
    print(f"\n✅ Валидация завершена")

if __name__ == '__main__':
    main()

