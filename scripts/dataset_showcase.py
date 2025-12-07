#!/usr/bin/env python3
"""
Витрина примеров датасета

Показывает примеры ответов с разными субскорами:
- Низкий GRA + реальные грамматические ошибки
- Высокий LR + разнообразная лексика
- Низкий FC + обрывы/self-correction
- Разные комбинации субскоров
"""

import csv
import random

def load_answers(filepath: str):
    """Загружает ответы из CSV"""
    answers = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                overall = float(row.get('target_band_overall', 0))
                if 3.0 <= overall <= 9.0:
                    answers.append(row)
            except:
                continue
    return answers

def find_examples_by_criteria(answers, criteria_func, max_examples=3):
    """Находит примеры по критерию"""
    matches = []
    for answer in answers:
        if criteria_func(answer):
            matches.append(answer)
            if len(matches) >= max_examples:
                break
    return matches

def main():
    print("=" * 70)
    print("ВИТРИНА ДАТАСЕТА: ПРИМЕРЫ С РАЗНЫМИ СУБСКОРАМИ")
    print("=" * 70)
    
    # Загружаем данные
    print("\n📂 Загрузка данных...")
    v1_0 = load_answers('dataset_versions/v1.0/answers.csv')
    print(f"   v1.0: {len(v1_0)} ответов")
    
    try:
        v1_1 = load_answers('answers_v1.1_preview.csv')
        print(f"   v1.1 preview: {len(v1_1)} ответов")
        all_answers = v1_0 + v1_1
    except:
        all_answers = v1_0
    
    print(f"   Всего: {len(all_answers)} ответов")
    
    examples = []
    
    # 1. Низкий GRA + грамматические ошибки
    print("\n🔍 Поиск примеров: Низкий GRA (≤5.0) с грамматическими ошибками...")
    def low_gra_with_errors(answer):
        try:
            gra = float(answer['target_band_gra'])
            text = (answer.get('answer_text', '') or answer.get('transcript_raw', '')).lower()
            # Проверяем наличие грамматических ошибок
            has_errors = any([
                'he go' in text or 'she do' in text or 'it make' in text,
                'i am agree' in text or 'i very like' in text,
                'i like book' in text or 'i go to school' in text and 'the' not in text[:50],
            ])
            return gra <= 5.0 and has_errors and len(text) > 20
        except:
            return False
    
    low_gra_examples = find_examples_by_criteria(all_answers, low_gra_with_errors, 3)
    if low_gra_examples:
        examples.append(("Низкий GRA с грамматическими ошибками", low_gra_examples))
    
    # 2. Высокий LR + разнообразная лексика
    print("🔍 Поиск примеров: Высокий LR (≥7.0) с продвинутой лексикой...")
    def high_lr_with_vocab(answer):
        try:
            lr = float(answer['target_band_lr'])
            text = (answer.get('answer_text', '') or answer.get('transcript_raw', '')).lower()
            # Проверяем наличие продвинутых слов
            advanced_words = ['appreciate', 'significant', 'fascinating', 'remarkable',
                            'extraordinary', 'challenging', 'accomplish', 'crucial']
            has_advanced = any(word in text for word in advanced_words)
            return lr >= 7.0 and has_advanced and len(text) > 30
        except:
            return False
    
    high_lr_examples = find_examples_by_criteria(all_answers, high_lr_with_vocab, 3)
    if high_lr_examples:
        examples.append(("Высокий LR с продвинутой лексикой", high_lr_examples))
    
    # 3. Низкий FC + обрывы/self-correction
    print("🔍 Поиск примеров: Низкий FC (≤5.0) с проблемами связности...")
    def low_fc_with_disfluency(answer):
        try:
            fc = float(answer['target_band_fc'])
            text = answer.get('answer_text', '') or answer.get('transcript_raw', '')
            # Проверяем наличие disfluency
            has_disfluency = any([
                '...' in text,
                'um' in text.lower() or 'uh' in text.lower(),
                'you know' in text.lower() or 'I mean' in text.lower(),
                text.count('...') >= 2,
            ])
            return fc <= 5.0 and has_disfluency and len(text) > 20
        except:
            return False
    
    low_fc_examples = find_examples_by_criteria(all_answers, low_fc_with_disfluency, 3)
    if low_fc_examples:
        examples.append(("Низкий FC с проблемами связности", low_fc_examples))
    
    # 4. Разнообразие субскоров (например, GRA низкий, но LR высокий)
    print("🔍 Поиск примеров: Разнообразие субскоров (GRA низкий, LR высокий)...")
    def varied_subscores(answer):
        try:
            gra = float(answer['target_band_gra'])
            lr = float(answer['target_band_lr'])
            fc = float(answer['target_band_fc'])
            pr = float(answer['target_band_pr'])
            # Ищем ответы с большим разбросом
            scores = [gra, lr, fc, pr]
            score_range = max(scores) - min(scores)
            return score_range >= 1.5 and len((answer.get('answer_text', '') or answer.get('transcript_raw', ''))) > 30
        except:
            return False
    
    varied_examples = find_examples_by_criteria(all_answers, varied_subscores, 3)
    if varied_examples:
        examples.append(("Разнообразие субскоров", varied_examples))
    
    # 5. Низкий LR + повторения
    print("🔍 Поиск примеров: Низкий LR (≤5.0) с лексическими ограничениями...")
    def low_lr_with_repetition(answer):
        try:
            lr = float(answer['target_band_lr'])
            text = (answer.get('answer_text', '') or answer.get('transcript_raw', '')).lower()
            words = text.split()
            if len(words) < 10:
                return False
            # Проверяем повторения
            unique_ratio = len(set(words)) / len(words)
            return lr <= 5.0 and unique_ratio < 0.7 and len(text) > 30
        except:
            return False
    
    low_lr_examples = find_examples_by_criteria(all_answers, low_lr_with_repetition, 3)
    if low_lr_examples:
        examples.append(("Низкий LR с лексическими ограничениями", low_lr_examples))
    
    # Выводим примеры
    print("\n" + "=" * 70)
    print("ПРИМЕРЫ")
    print("=" * 70)
    
    for category, category_examples in examples:
        print(f"\n{'='*70}")
        print(f"📌 {category.upper()}")
        print(f"{'='*70}")
        
        for i, example in enumerate(category_examples[:2], 1):  # Показываем по 2 примера
            try:
                overall = float(example['target_band_overall'])
                fc = float(example['target_band_fc'])
                lr = float(example['target_band_lr'])
                gra = float(example['target_band_gra'])
                pr = float(example['target_band_pr'])
                
                text = example.get('answer_text', '') or example.get('transcript_raw', '')
                question = example.get('question_text', 'N/A')
                part = example.get('part', '?')
                
                print(f"\n   Пример {i} (Part {part}):")
                print(f"   Вопрос: {question}")
                print(f"   Ответ: {text[:200]}{'...' if len(text) > 200 else ''}")
                print(f"   Subscores: Overall={overall}, FC={fc}, LR={lr}, GRA={gra}, PR={pr}")
                print(f"   Source: {example.get('source_type', 'unknown')}")
            except Exception as e:
                print(f"   ⚠️  Ошибка при обработке примера: {e}")
    
    # Сохраняем в markdown
    print("\n" + "=" * 70)
    print("💾 Сохранение витрины в DATASET_SHOWCASE.md...")
    
    with open('DATASET_SHOWCASE.md', 'w', encoding='utf-8') as f:
        f.write("# Витрина датасета IELTS Speaking\n\n")
        f.write("Примеры ответов с разными характеристиками субскоров.\n\n")
        
        for category, category_examples in examples:
            f.write(f"## {category}\n\n")
            
            for i, example in enumerate(category_examples[:2], 1):
                try:
                    overall = float(example['target_band_overall'])
                    fc = float(example['target_band_fc'])
                    lr = float(example['target_band_lr'])
                    gra = float(example['target_band_gra'])
                    pr = float(example['target_band_pr'])
                    
                    text = example.get('answer_text', '') or example.get('transcript_raw', '')
                    question = example.get('question_text', 'N/A')
                    part = example.get('part', '?')
                    
                    f.write(f"### Пример {i} (Part {part})\n\n")
                    f.write(f"**Вопрос:** {question}\n\n")
                    f.write(f"**Ответ:**\n\n")
                    f.write(f"> {text}\n\n")
                    f.write(f"**Subscores:**\n")
                    f.write(f"- Overall: {overall}\n")
                    f.write(f"- FC (Fluency & Coherence): {fc}\n")
                    f.write(f"- LR (Lexical Resource): {lr}\n")
                    f.write(f"- GRA (Grammatical Range & Accuracy): {gra}\n")
                    f.write(f"- PR (Pronunciation): {pr}\n\n")
                    f.write(f"**Source:** {example.get('source_type', 'unknown')}\n\n")
                    f.write("---\n\n")
                except:
                    pass
    
    print("✅ Витрина сохранена в DATASET_SHOWCASE.md")

if __name__ == '__main__':
    main()

