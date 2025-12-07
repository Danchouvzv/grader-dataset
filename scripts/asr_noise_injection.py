#!/usr/bin/env python3
"""
ASR Noise Injection Script (Tier 3 Augmentation)

Добавляет реалистичные ASR-артефакты в ответы:
- Filler words ("um", "uh", "like", "you know")
- Повторения
- Пропуски
- ASR-перепутки
- Отсутствие пунктуации
- Conflated clauses
"""

import csv
import random
import re

# Filler words для разных уровней
FILLER_WORDS = ["um", "uh", "like", "you know", "well", "actually", "I mean"]

# ASR-перепутки (common mistakes)
ASR_MISTAKES = {
    "gym": "jim",
    "beach": "bitch",
    "think": "thing",
    "three": "tree",
    "through": "true",
    "their": "there",
    "they're": "there",
    "then": "than",
    "its": "it's",
    "your": "you're",
}

def add_filler_words(text: str, level: float) -> str:
    """Добавляет filler words в зависимости от уровня"""
    words = text.split()
    
    if level <= 4.0:
        # Много filler words для низких уровней
        filler_prob = 0.15
        filler_count = random.randint(3, 6)
    elif level <= 5.5:
        filler_prob = 0.10
        filler_count = random.randint(2, 4)
    elif level <= 6.5:
        filler_prob = 0.05
        filler_count = random.randint(1, 3)
    else:
        filler_prob = 0.02
        filler_count = random.randint(0, 2)
    
    if random.random() < filler_prob:
        # Добавляем filler words в случайные места
        for _ in range(filler_count):
            if len(words) > 0:
                pos = random.randint(0, len(words))
                filler = random.choice(FILLER_WORDS)
                words.insert(pos, f"{filler}...")
    
    return " ".join(words)

def add_repetitions(text: str, level: float) -> str:
    """Добавляет повторения (характерно для низких уровней)"""
    if level > 6.0:
        return text
    
    words = text.split()
    if len(words) < 3:
        return text
    
    # Для низких уровней больше повторений
    if level <= 4.0 and random.random() < 0.3:
        # Повторяем первое слово
        first_word = words[0]
        words.insert(0, f"{first_word}...")
        words.insert(1, f"{first_word}...")
    elif level <= 5.5 and random.random() < 0.15:
        # Одно повторение
        word = random.choice(words[:5])
        pos = words.index(word) + 1
        words.insert(pos, f"{word}...")
    
    return " ".join(words)

def add_asr_mistakes(text: str, level: float) -> str:
    """Добавляет ASR-перепутки"""
    if level > 7.0:
        return text  # Высокие уровни реже имеют ASR-ошибки
    
    # Вероятность ошибки зависит от уровня
    if level <= 4.0:
        mistake_prob = 0.2
    elif level <= 5.5:
        mistake_prob = 0.1
    else:
        mistake_prob = 0.05
    
    for correct, mistake in ASR_MISTAKES.items():
        if random.random() < mistake_prob and correct.lower() in text.lower():
            # Заменяем с учетом регистра
            pattern = re.compile(re.escape(correct), re.IGNORECASE)
            if random.random() < 0.5:  # 50% шанс заменить
                text = pattern.sub(mistake, text, count=1)
    
    return text

def remove_punctuation(text: str, level: float) -> str:
    """Убирает пунктуацию (характерно для ASR)"""
    if level > 6.5:
        return text  # Высокие уровни обычно имеют пунктуацию
    
    # Убираем запятые и точки, но оставляем основные знаки
    if level <= 5.0 and random.random() < 0.4:
        text = text.replace(",", "")
        text = text.replace(".", "")
        text = text.replace(";", "")
        text = text.replace(":", "")
    
    return text

def add_pauses(text: str, level: float) -> str:
    """Добавляет паузы (многоточия)"""
    if level > 7.0:
        return text
    
    words = text.split()
    
    if level <= 4.0:
        pause_prob = 0.25
        pause_count = random.randint(2, 4)
    elif level <= 5.5:
        pause_prob = 0.15
        pause_count = random.randint(1, 3)
    else:
        pause_prob = 0.08
        pause_count = random.randint(0, 2)
    
    if random.random() < pause_prob:
        for _ in range(pause_count):
            if len(words) > 2:
                pos = random.randint(1, len(words) - 1)
                words.insert(pos, "...")
    
    return " ".join(words)

def add_conflated_clauses(text: str, level: float) -> str:
    """Добавляет conflated clauses (характерно для низких уровней)"""
    if level > 6.0:
        return text
    
    if level <= 5.0 and random.random() < 0.2:
        # Добавляем "and" между предложениями
        text = text.replace(". ", " and ")
        text = text.replace(", ", " and ")
    
    return text

def inject_asr_noise(text: str, overall: float) -> str:
    """Основная функция для инъекции ASR-шумов"""
    # Применяем все типы шумов
    text = add_filler_words(text, overall)
    text = add_repetitions(text, overall)
    text = add_pauses(text, overall)
    text = add_asr_mistakes(text, overall)
    text = remove_punctuation(text, overall)
    text = add_conflated_clauses(text, overall)
    
    return text

def main():
    print("=" * 70)
    print("ASR NOISE INJECTION (Tier 3 Augmentation)")
    print("=" * 70)
    
    # Загружаем ответы
    print("\n📂 Загрузка ответов...")
    with open('answers.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        answers = list(reader)
    
    print(f"   Загружено: {len(answers)} ответов")
    
    # Выбираем ответы для augmentation (не все, чтобы сохранить разнообразие)
    # Берем 30% ответов для добавления ASR noise
    target_count = int(len(answers) * 0.3)
    selected_answers = random.sample(answers, min(target_count, len(answers)))
    
    print(f"\n🎯 Выбрано {len(selected_answers)} ответов для ASR noise injection")
    
    # Получаем следующий answer_id
    max_answer_id = 0
    for answer in answers:
        try:
            ans_num = int(answer['answer_id'].split('_')[1])
            max_answer_id = max(max_answer_id, ans_num)
        except:
            pass
    
    next_answer_id = max_answer_id + 1
    
    # Создаем новые ответы с ASR noise
    new_answers = []
    
    print(f"\n🔧 Применение ASR noise injection...")
    
    for answer in selected_answers:
        try:
            overall = float(answer['target_band_overall'])
            original_text = answer['answer_text']
            
            # Применяем ASR noise
            noisy_text = inject_asr_noise(original_text, overall)
            
            # Создаем новый ответ (копия с шумом)
            new_answer = answer.copy()
            new_answer['answer_id'] = f'ans_{next_answer_id:03d}'
            new_answer['answer_text'] = noisy_text
            new_answer['transcript_raw'] = noisy_text
            new_answer['source_type'] = 'synthetic_augmented'
            
            # Немного снижаем субскоры из-за шума (реалистично)
            fc = float(answer['target_band_fc'])
            lr = float(answer['target_band_lr'])
            gra = float(answer['target_band_gra'])
            pr = float(answer['target_band_pr'])
            
            # Небольшое снижение FC и PR из-за шума
            if overall <= 6.0:
                fc = max(3.0, fc - 0.5)
                pr = max(3.0, pr - 0.5)
            
            new_answer['target_band_fc'] = str(fc)
            new_answer['target_band_pr'] = str(pr)
            
            new_answers.append(new_answer)
            next_answer_id += 1
            
        except Exception as e:
            print(f"   ⚠️ Ошибка при обработке {answer.get('answer_id', 'unknown')}: {e}")
            continue
    
    # Сохраняем новые ответы
    print(f"\n💾 Сохранение {len(new_answers)} новых ответов с ASR noise...")
    
    with open('answers.csv', 'a', encoding='utf-8', newline='') as f:
        fieldnames = ['answer_id', 'session_id', 'user_id', 'part', 'question_id', 'question_text',
                     'answer_text', 'duration_sec', 'target_band_overall', 'target_band_fc',
                     'target_band_lr', 'target_band_gra', 'target_band_pr', 'transcript_raw',
                     'source_type', 'quality_flag']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(new_answers)
    
    # Статистика
    print("\n" + "=" * 70)
    print("✅ СТАТИСТИКА")
    print("=" * 70)
    print(f"   ✅ Добавлено ответов с ASR noise: {len(new_answers)}")
    
    # Проверка примеров
    print(f"\n📋 Примеры ASR noise injection:")
    for i, answer in enumerate(new_answers[:3]):
        print(f"\n   Пример {i+1} (overall={answer['target_band_overall']}):")
        print(f"   Оригинал: {answer.get('transcript_raw', answer['answer_text'])[:100]}...")
        print(f"   С шумом:  {answer['answer_text'][:100]}...")
    
    print("\n✅ ASR noise injection завершен!")

if __name__ == '__main__':
    main()

