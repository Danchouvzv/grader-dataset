#!/usr/bin/env python3
"""
Error Injection Module (Tier 2 Augmentation)

Привязка ошибок к субскорам:
- GRA низкий → грамматические ошибки
- LR низкий → лексические ограничения
- FC низкий → проблемы со связностью
- PR низкий → ASR-артефакты (уже частично в asr_noise_injection.py)
"""

import random
import re
from typing import Tuple

# Грамматические ошибки по severity
GRAMMAR_ERRORS = {
    "high": [
        # Third person
        ("he go", "he goes"), ("she like", "she likes"), ("it make", "it makes"),
        ("he do", "he does"), ("she have", "she has"), ("it take", "it takes"),
        
        # Articles
        ("I like book", "I like the book"), ("I go to school", "I go to the school"),
        ("I see movie", "I see a movie"), ("I have car", "I have a car"),
        
        # Tenses
        ("I go yesterday", "I went yesterday"), ("I see him tomorrow", "I will see him tomorrow"),
        ("I am go", "I go"), ("I was go", "I went"), ("I will went", "I will go"),
        
        # Word order
        ("I very like", "I like very much"), ("I don't know what do", "I don't know what to do"),
        ("I am agree", "I agree"), ("I am not sure what is", "I am not sure what it is"),
        
        # Prepositions
        ("I go in school", "I go to school"), ("I listen music", "I listen to music"),
        ("I depend from", "I depend on"), ("I interested in", "I am interested in"),
    ],
    "medium": [
        # Менее частые ошибки
        ("he doesn't goes", "he doesn't go"), ("she didn't went", "she didn't go"),
        ("I have been go", "I have been going"), ("I would went", "I would go"),
        ("more better", "better"), ("most good", "best"),
    ],
    "low": [
        # Редкие, тонкие ошибки
        ("less people", "fewer people"), ("between you and I", "between you and me"),
    ]
}

# Лексические ограничения по severity
LEXICAL_LIMITATIONS = {
    "high": {
        # Замены продвинутых слов на простые
        "enjoy": "like",
        "appreciate": "like",
        "significant": "important",
        "crucial": "important",
        "essential": "important",
        "fascinating": "interesting",
        "remarkable": "good",
        "extraordinary": "very good",
        "challenging": "difficult",
        "accomplish": "do",
        "achieve": "do",
        "obtain": "get",
        "acquire": "get",
    },
    "medium": {
        "wonderful": "good",
        "excellent": "good",
        "terrible": "bad",
        "enormous": "big",
        "tiny": "small",
    },
    "low": {
        # Минимальные замены
        "fantastic": "great",
        "incredible": "amazing",
    }
}

# Повтор слов для низкого LR
REPETITION_PATTERNS = {
    "high": 0.4,  # 40% шанс повторить слово
    "medium": 0.2,
    "low": 0.1,
}

# Проблемы со связностью для низкого FC
FC_DISFLUENCY = {
    "high": [
        "um...", "uh...", "you know...", "I mean...", "like...",
        "actually, wait...", "let me think...", "what I want to say is...",
    ],
    "medium": [
        "well...", "actually...", "I guess...", "kind of...",
    ],
    "low": [
        "well,", "actually,", "I suppose,",
    ]
}

def get_severity(score: float, threshold_low: float = 4.5, threshold_high: float = 6.5) -> str:
    """Определяет severity на основе субскора"""
    if score <= threshold_low:
        return "high"
    elif score <= threshold_high:
        return "medium"
    else:
        return "low"

def inject_grammar_errors(text: str, gra: float) -> str:
    """Добавляет грамматические ошибки в зависимости от GRA"""
    severity = get_severity(gra, threshold_low=4.5, threshold_high=6.0)
    
    if severity == "low":
        return text  # Высокий GRA - минимум ошибок
    
    errors = GRAMMAR_ERRORS[severity]
    
    # Количество ошибок зависит от severity
    if severity == "high":
        max_errors = random.randint(2, 4)
        error_prob = 0.4
    elif severity == "medium":
        max_errors = random.randint(1, 2)
        error_prob = 0.2
    else:
        max_errors = 1
        error_prob = 0.1
    
    error_count = 0
    text_lower = text.lower()
    
    for wrong, correct in errors:
        if error_count >= max_errors:
            break
        
        if correct.lower() in text_lower and random.random() < error_prob:
            # Заменяем с учетом регистра
            pattern = re.compile(re.escape(correct), re.IGNORECASE)
            matches = list(pattern.finditer(text))
            if matches:
                match = random.choice(matches)
                # Заменяем только первое вхождение
                text = text[:match.start()] + wrong + text[match.end():]
                error_count += 1
                text_lower = text.lower()
    
    return text

def inject_lexical_limits(text: str, lr: float) -> str:
    """Ограничивает лексику в зависимости от LR"""
    severity = get_severity(lr, threshold_low=5.0, threshold_high=6.5)
    
    if severity == "low":
        return text  # Высокий LR - разнообразная лексика
    
    limitations = LEXICAL_LIMITATIONS[severity]
    
    # Заменяем продвинутые слова на простые
    for advanced, simple in limitations.items():
        if advanced in text.lower():
            # Заменяем с учетом регистра
            pattern = re.compile(r'\b' + re.escape(advanced) + r'\b', re.IGNORECASE)
            if random.random() < 0.6:  # 60% шанс заменить
                text = pattern.sub(simple, text)
    
    # Добавляем повторения для очень низкого LR
    if severity == "high" and random.random() < REPETITION_PATTERNS["high"]:
        words = text.split()
        if len(words) > 3:
            # Повторяем одно из первых слов
            word_to_repeat = random.choice(words[:5])
            pos = words.index(word_to_repeat) + 1
            words.insert(pos, f"{word_to_repeat}...")
            text = " ".join(words)
    
    return text

def inject_fc_disfluency(text: str, fc: float) -> str:
    """Добавляет проблемы со связностью в зависимости от FC"""
    severity = get_severity(fc, threshold_low=4.5, threshold_high=6.0)
    
    if severity == "low":
        return text  # Высокий FC - хорошая связность
    
    disfluencies = FC_DISFLUENCY[severity]
    
    # Количество disfluencies зависит от severity
    if severity == "high":
        count = random.randint(2, 4)
        prob = 0.5
    elif severity == "medium":
        count = random.randint(1, 2)
        prob = 0.3
    else:
        count = 1
        prob = 0.15
    
    if random.random() < prob:
        words = text.split()
        
        for _ in range(count):
            if len(words) > 2:
                disfluency = random.choice(disfluencies)
                # Добавляем в случайное место
                pos = random.randint(1, len(words) - 1)
                words.insert(pos, disfluency)
        
        text = " ".join(words)
    
    # Добавляем обрывы мыслей для очень низкого FC
    if severity == "high" and random.random() < 0.3:
        # Добавляем "..." в конце предложений
        text = re.sub(r'\.\s+', '... ', text)
        # Иногда обрываем на середине
        if random.random() < 0.2:
            words = text.split()
            if len(words) > 5:
                cut_pos = random.randint(len(words) // 2, len(words) - 2)
                text = " ".join(words[:cut_pos]) + "..."
    
    return text

def inject_errors_by_subscores(text: str, fc: float, lr: float, gra: float, pr: float) -> str:
    """Основная функция: добавляет ошибки в зависимости от всех субскоров"""
    # Применяем ошибки по каждому критерию
    text = inject_grammar_errors(text, gra)
    text = inject_lexical_limits(text, lr)
    text = inject_fc_disfluency(text, fc)
    
    # PR уже обрабатывается в asr_noise_injection.py, но можно добавить дополнительные артефакты
    if pr <= 5.0:
        # Добавляем больше filler words для низкого PR
        fillers = ["um", "uh", "er", "erm"]
        if random.random() < 0.3:
            words = text.split()
            if len(words) > 2:
                filler = random.choice(fillers)
                pos = random.randint(1, len(words) - 1)
                words.insert(pos, f"{filler}...")
                text = " ".join(words)
    
    return text

def main():
    """Тестирование error injection"""
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ERROR INJECTION")
    print("=" * 70)
    
    test_cases = [
        ("I really enjoy reading books in my free time.", 4.0, 4.0, 4.0, 4.5, 5.0),  # Все низкие
        ("I find this topic quite fascinating and significant.", 6.0, 5.0, 7.0, 6.5, 6.0),  # LR низкий
        ("He goes to school every day and enjoys learning.", 6.0, 7.0, 4.5, 6.5, 6.0),  # GRA низкий
        ("I think this is important. It helps people. It makes life better.", 4.5, 6.0, 6.5, 6.0, 5.5),  # FC низкий
        ("I absolutely appreciate this remarkable opportunity.", 7.0, 7.5, 7.5, 7.0, 7.0),  # Все высокие
    ]
    
    for original, overall, fc, lr, gra, pr in test_cases:
        print(f"\n📝 Оригинал: {original}")
        print(f"   Subscores: FC={fc}, LR={lr}, GRA={gra}, PR={pr}")
        
        modified = inject_errors_by_subscores(original, fc, lr, gra, pr)
        print(f"   С ошибками: {modified}")
        
        if original != modified:
            print(f"   ✅ Изменения применены")
        else:
            print(f"   ⚠️  Без изменений (возможно, все субскоры высокие)")

if __name__ == '__main__':
    main()

