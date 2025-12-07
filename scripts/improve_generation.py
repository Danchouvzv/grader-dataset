#!/usr/bin/env python3
"""
Улучшенная генерация ответов с:
- Больше вариативности (5-8 шаблонов на диапазон)
- Правильное извлечение темы (topic_noun/topic_phrase)
- Дискурсивные маркеры
- Привязка ошибок к субскорам
- Улучшенная логика quality_flag
"""

import csv
import random
import re
from typing import List, Tuple, Dict

# Дискурсивные маркеры для разных уровней
DISCOURSE_MARKERS_LOW = ["um", "uh", "well", "actually", "I think", "you know"]
DISCOURSE_MARKERS_MID = ["well", "actually", "to be honest", "I guess", "I mean", "kind of", "I'd say"]
DISCOURSE_MARKERS_HIGH = ["actually", "to be honest", "I suppose", "I'd say", "frankly", "in fact"]

# Грамматические ошибки для низкого GRA
GRAMMAR_ERRORS = {
    "third_person": [("he go", "he goes"), ("she like", "she likes"), ("it make", "it makes")],
    "articles": [("I like book", "I like the book"), ("I go to school", "I go to the school")],
    "tenses": [("I go yesterday", "I went yesterday"), ("I see him tomorrow", "I will see him tomorrow")],
    "word_order": [("I very like", "I like very much"), ("I don't know what to do", "I don't know what do")],
}

# Лексические ограничения для низкого LR
LEXICAL_REPETITION = {
    "good": ["good", "nice", "fine", "okay"],
    "like": ["like", "enjoy", "love"],
    "think": ["think", "believe", "feel"],
    "important": ["important", "significant", "crucial"],
}

def extract_topic_from_question(question: str) -> str:
    """Улучшенное извлечение темы из вопроса"""
    question_lower = question.lower()
    
    # Специфичные паттерны для разных типов вопросов
    if "do you like" in question_lower or "do you enjoy" in question_lower:
        # "Do you like listening to music?" -> "listening to music"
        match = re.search(r'(?:like|enjoy)\s+(.+?)\?', question_lower)
        if match:
            topic = match.group(1).strip()
            # Убираем лишние слова
            topic = re.sub(r'\b(do|you|to|the|a|an)\b', '', topic).strip()
            return topic if topic else "it"
    
    if "what kind of" in question_lower:
        # "What kind of music do you listen to?" -> "music"
        match = re.search(r'what kind of (\w+)', question_lower)
        if match:
            return match.group(1)
    
    if "how often" in question_lower:
        # "How often do you use social media?" -> "social media"
        match = re.search(r'how often do you (.+?)\?', question_lower)
        if match:
            topic = match.group(1).strip()
            # Убираем "use" если есть
            topic = re.sub(r'\buse\b', '', topic).strip()
            return topic if topic else "it"
    
    if "what's your" in question_lower or "what is your" in question_lower:
        # "What's your favorite season?" -> "season"
        match = re.search(r'(?:what\'s|what is) your (.+?)\?', question_lower)
        if match:
            topic = match.group(1).strip()
            # Убираем "favorite" если есть
            topic = re.sub(r'\bfavorite\b', '', topic).strip()
            return topic if topic else "it"
    
    if "how do you" in question_lower:
        # "How do you relax?" -> "relaxing"
        match = re.search(r'how do you (.+?)\?', question_lower)
        if match:
            verb = match.group(1).strip()
            # Преобразуем глагол в -ing форму если нужно
            if not verb.endswith('ing'):
                if verb.endswith('e'):
                    verb = verb[:-1] + 'ing'
                else:
                    verb = verb + 'ing'
            return verb
    
    # Fallback: берем последнее слово
    words = question.split()
    if words:
        return words[-1].rstrip('?')
    
    return "it"

def add_grammar_errors(text: str, gra: float) -> str:
    """Добавляет грамматические ошибки в зависимости от GRA"""
    if gra >= 6.5:
        return text  # Высокий GRA - минимум ошибок
    
    words = text.split()
    error_count = 0
    
    if gra <= 4.0:
        # Много ошибок
        max_errors = random.randint(2, 4)
        error_prob = 0.3
    elif gra <= 5.5:
        # Умеренные ошибки
        max_errors = random.randint(1, 2)
        error_prob = 0.15
    else:
        # Редкие ошибки
        max_errors = 1
        error_prob = 0.05
    
    # Добавляем ошибки третьего лица
    if gra <= 5.5 and random.random() < error_prob:
        for wrong, correct in GRAMMAR_ERRORS["third_person"]:
            if correct in text.lower() and error_count < max_errors:
                text = text.replace(correct, wrong, 1)
                error_count += 1
    
    # Добавляем ошибки с артиклями
    if gra <= 5.0 and random.random() < error_prob:
        for wrong, correct in GRAMMAR_ERRORS["articles"]:
            if correct.lower() in text.lower() and error_count < max_errors:
                text = re.sub(re.escape(correct), wrong, text, flags=re.IGNORECASE, count=1)
                error_count += 1
    
    # Добавляем ошибки времен
    if gra <= 5.5 and random.random() < error_prob:
        for wrong, correct in GRAMMAR_ERRORS["tenses"]:
            if correct.lower() in text.lower() and error_count < max_errors:
                text = re.sub(re.escape(correct), wrong, text, flags=re.IGNORECASE, count=1)
                error_count += 1
    
    return text

def add_lexical_limitations(text: str, lr: float) -> str:
    """Ограничивает лексику в зависимости от LR"""
    if lr >= 7.0:
        return text  # Высокий LR - разнообразная лексика
    
    if lr <= 5.0:
        # Низкий LR - повтор простых слов
        for simple_word, alternatives in LEXICAL_REPETITION.items():
            if simple_word in text.lower():
                # Заменяем альтернативы на простое слово
                for alt in alternatives:
                    if alt != simple_word and alt in text.lower():
                        text = re.sub(r'\b' + re.escape(alt) + r'\b', simple_word, text, flags=re.IGNORECASE)
    
    return text

def add_discourse_markers(text: str, overall: float) -> str:
    """Добавляет дискурсивные маркеры в зависимости от уровня"""
    if overall <= 4.5:
        markers = DISCOURSE_MARKERS_LOW
        prob = 0.4
    elif overall <= 6.5:
        markers = DISCOURSE_MARKERS_MID
        prob = 0.3
    else:
        markers = DISCOURSE_MARKERS_HIGH
        prob = 0.2
    
    if random.random() < prob:
        marker = random.choice(markers)
        # Добавляем только в начало (более естественно)
        if not text[0].isupper():
            text = text[0].upper() + text[1:]
        text = f"{marker}, {text}"
    
    return text

def determine_quality_flag(overall: float) -> str:
    """Улучшенная логика quality_flag"""
    if overall <= 3.5:
        return 'garbage'
    elif overall <= 4.5:
        return 'ok_low'  # Простые, но не garbage
    else:
        return 'ok'

def generate_part1_answer_improved(question: str, overall: float, fc: float, lr: float, gra: float, pr: float) -> Tuple[str, int]:
    """Улучшенная генерация ответов Part 1 с вариативностью и привязкой к субскорам"""
    topic = extract_topic_from_question(question)
    
    # Длительность зависит от уровня
    if overall <= 4.5:
        duration = random.randint(8, 18)
    elif overall <= 6.5:
        duration = random.randint(12, 22)
    else:
        duration = random.randint(18, 28)
    
    # Множество шаблонов для каждого диапазона
    if overall <= 4.0:
        templates = [
            f"I like {topic}. It is good.",
            f"Yes, I like it. It is... um... nice.",
            f"I think... {topic}... is good.",
            f"Yes, I do. I like it very much.",
            f"I like {topic} because it is good for me.",
            f"{topic} is good. I like it.",
            f"I think {topic} is nice thing.",
            f"Yes, I like {topic}. It make me happy.",
        ]
        
    elif overall <= 5.0:
        templates = [
            f"Yes, I do like {topic}. I think it is interesting and I enjoy it.",
            f"I really like {topic}. It makes me happy and I do it often.",
            f"Yes, I enjoy {topic}. It is one of my favorite things to do.",
            f"Well, I like {topic} quite a bit. I think it is fun and I do it when I have time.",
            f"Actually, I really enjoy {topic}. It is something I like to do in my free time.",
            f"I guess I like {topic}. It is interesting and I think it is good for me.",
            f"To be honest, I do like {topic}. I find it enjoyable and I do it regularly.",
        ]
        
    elif overall <= 6.0:
        templates = [
            f"Yes, I do enjoy {topic}. I find it quite relaxing and it helps me unwind after a busy day.",
            f"I really like {topic}. It's something I do regularly, especially on weekends when I have more free time.",
            f"Absolutely, I'm quite fond of {topic}. I think it's a great way to spend my leisure time and I always look forward to it.",
            f"Well, I'd say I really enjoy {topic}. I find it both interesting and relaxing, and it's become a regular part of my routine.",
            f"Actually, I'm quite passionate about {topic}. I think it's a wonderful way to relax and I try to make time for it whenever possible.",
            f"To be honest, I really like {topic}. It's something that brings me joy and helps me feel more balanced in my daily life.",
            f"I guess I'd say I enjoy {topic}. I find it quite engaging and it's definitely one of my preferred ways to spend free time.",
        ]
        
    elif overall <= 7.0:
        templates = [
            f"Yes, I absolutely enjoy {topic}. I find it both intellectually stimulating and personally rewarding. It's become an integral part of my daily routine.",
            f"I'm quite passionate about {topic}. I appreciate how it allows me to explore different perspectives and continuously learn new things.",
            f"Definitely, I'm very enthusiastic about {topic}. It's something that brings me both relaxation and a sense of accomplishment.",
            f"To be honest, I have a genuine appreciation for {topic}. It's something I've cultivated over time, and it continues to be a source of both inspiration and satisfaction.",
            f"Actually, I'm deeply engaged with {topic}. I find that it provides a unique combination of challenge and enjoyment that keeps me motivated.",
            f"I'd say I'm quite passionate about {topic}. It's become a fundamental aspect of how I approach life, offering both intellectual enrichment and personal fulfillment.",
        ]
        
    else:
        templates = [
            f"I have a genuine appreciation for {topic}. It's become a fundamental aspect of how I approach life, offering both intellectual enrichment and personal fulfillment.",
            f"Absolutely, I'm deeply engaged with {topic}. I find that it provides a unique combination of challenge and enjoyment that keeps me motivated.",
            f"Yes, I'm quite passionate about {topic}. It's something I've cultivated over time, and it continues to be a source of both inspiration and satisfaction.",
        ]
    
    # Выбираем шаблон
    answer = random.choice(templates)
    
    # Добавляем дискурсивные маркеры
    answer = add_discourse_markers(answer, overall)
    
    # Добавляем грамматические ошибки в зависимости от GRA
    answer = add_grammar_errors(answer, gra)
    
    # Ограничиваем лексику в зависимости от LR
    answer = add_lexical_limitations(answer, lr)
    
    return answer, duration

def main():
    """Тестирование улучшенной генерации"""
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ ГЕНЕРАЦИИ")
    print("=" * 70)
    
    test_questions = [
        "Do you like listening to music?",
        "How often do you use social media?",
        "What's your favorite season?",
        "How do you relax after work?",
    ]
    
    test_cases = [
        (4.0, 4.0, 3.5, 4.0, 4.5),  # Низкий уровень, низкий GRA
        (5.5, 5.5, 4.5, 6.0, 5.5),  # Средний, низкий GRA
        (6.0, 6.5, 5.5, 7.0, 6.0),  # Средний, низкий LR
        (7.0, 7.5, 8.0, 6.5, 7.0),  # Высокий, низкий GRA
    ]
    
    for question in test_questions:
        print(f"\n📝 Вопрос: {question}")
        print(f"   Тема: {extract_topic_from_question(question)}")
        
        for overall, fc, lr, gra, pr in test_cases:
            answer, duration = generate_part1_answer_improved(question, overall, fc, lr, gra, pr)
            quality = determine_quality_flag(overall)
            print(f"\n   Overall={overall}, FC={fc}, LR={lr}, GRA={gra}, PR={pr}, Quality={quality}")
            print(f"   Ответ: {answer}")
            print(f"   Длительность: {duration} сек")

if __name__ == '__main__':
    main()

