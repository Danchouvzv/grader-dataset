#!/usr/bin/env python3
"""
Human Sanity Check для Part 3
Выбирает примеры по бэндам для ручной проверки
"""

import csv
import random
from collections import defaultdict

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
]

def check_academic_phrases(text: str) -> list:
    """Проверяет наличие академических фраз"""
    text_lower = text.lower()
    found = []
    for phrase in ACADEMIC_RED_FLAGS:
        if phrase.lower() in text_lower:
            found.append(phrase)
    return found

def count_words(text: str) -> int:
    """Считает количество слов"""
    return len(text.split())

def main():
    print("=" * 70)
    print("HUMAN SANITY CHECK: ВЫБОРКА ПРИМЕРОВ ПО БЭНДАМ")
    print("=" * 70)
    
    filepath = 'dataset_versions/v1.2/answers.csv'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        answers = list(csv.DictReader(f))
    
    # Фильтруем Part 3
    part3 = [a for a in answers if a['part'] == '3']
    print(f"\n📊 Part 3 ответов: {len(part3)}")
    
    # Группируем по бэндам
    by_band = defaultdict(list)
    for a in part3:
        try:
            band = float(a['target_band_overall'])
            # Округляем до 0.5 для группировки
            band_rounded = round(band * 2) / 2
            by_band[band_rounded].append(a)
        except:
            continue
    
    # Выбираем примеры для проверки
    target_bands = [
        (4.0, 4.5),  # Low
        (5.5,),      # Mid-Low
        (6.5,),      # Mid-High
        (7.5, 8.0)   # High
    ]
    
    print("\n🔍 ВЫБОРКА ДЛЯ РУЧНОЙ ПРОВЕРКИ:")
    print("=" * 70)
    
    samples = []
    
    for band_group in target_bands:
        for target_band in band_group:
            if target_band in by_band:
                candidates = by_band[target_band]
                # Выбираем 3-5 случайных
                sample_size = min(5, len(candidates))
                selected = random.sample(candidates, sample_size)
                samples.extend(selected)
    
    # Сортируем по бэнду
    samples.sort(key=lambda x: float(x['target_band_overall']))
    
    # Выводим примеры
    for i, sample in enumerate(samples, 1):
        overall = float(sample['target_band_overall'])
        fc = float(sample['target_band_fc'])
        lr = float(sample['target_band_lr'])
        gra = float(sample['target_band_gra'])
        pr = float(sample['target_band_pr'])
        
        question = sample.get('question_text', '')
        answer = sample.get('answer_text', '')
        word_count = count_words(answer)
        
        # Проверки
        academic_phrases = check_academic_phrases(answer)
        is_suspicious = len(academic_phrases) > 0 or word_count > 70
        
        print(f"\n{'='*70}")
        print(f"Пример {i} | Overall: {overall} | FC: {fc}, LR: {lr}, GRA: {gra}, PR: {pr}")
        print(f"{'='*70}")
        print(f"Вопрос: {question}")
        print(f"\nОтвет ({word_count} слов):")
        print(f"{answer}")
        
        if academic_phrases:
            print(f"\n⚠️  НАЙДЕНЫ АКАДЕМИЧЕСКИЕ ФРАЗЫ:")
            for phrase in academic_phrases:
                print(f"   - {phrase}")
        
        if word_count > 70:
            print(f"\n⚠️  СЛИШКОМ ДЛИННО (>{word_count} слов) - похоже на эссе")
        elif word_count < 30:
            print(f"\n⚠️  СЛИШКОМ КОРОТКО (<{word_count} слов)")
        
        if is_suspicious:
            print(f"\n🔴 ПОДОЗРИТЕЛЬНЫЙ ОТВЕТ - требует проверки")
    
    # Статистика по проблемам
    print("\n" + "=" * 70)
    print("СТАТИСТИКА ПРОБЛЕМ")
    print("=" * 70)
    
    total_checked = len(samples)
    academic_count = sum(1 for s in samples if check_academic_phrases(s.get('answer_text', '')))
    long_count = sum(1 for s in samples if count_words(s.get('answer_text', '')) > 70)
    short_count = sum(1 for s in samples if count_words(s.get('answer_text', '')) < 30)
    
    print(f"\nПроверено примеров: {total_checked}")
    print(f"С академическими фразами: {academic_count} ({academic_count/total_checked*100:.1f}%)")
    print(f"Слишком длинных (>70 слов): {long_count} ({long_count/total_checked*100:.1f}%)")
    print(f"Слишком коротких (<30 слов): {short_count} ({short_count/total_checked*100:.1f}%)")
    
    # Сохраняем выборку в файл
    output_file = 'docs/human_sanity_check_samples.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("HUMAN SANITY CHECK: ВЫБОРКА ПРИМЕРОВ\n")
        f.write("=" * 70 + "\n\n")
        
        for i, sample in enumerate(samples, 1):
            f.write(f"\n{'='*70}\n")
            f.write(f"Пример {i}\n")
            f.write(f"Overall: {sample['target_band_overall']}\n")
            f.write(f"FC: {sample['target_band_fc']}, LR: {sample['target_band_lr']}, ")
            f.write(f"GRA: {sample['target_band_gra']}, PR: {sample['target_band_pr']}\n")
            f.write(f"{'='*70}\n")
            f.write(f"Вопрос: {sample.get('question_text', '')}\n\n")
            f.write(f"Ответ:\n{sample.get('answer_text', '')}\n\n")
    
    print(f"\n💾 Выборка сохранена в {output_file}")

if __name__ == '__main__':
    random.seed(42)
    main()

