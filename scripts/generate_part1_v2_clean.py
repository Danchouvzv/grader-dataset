#!/usr/bin/env python3
"""
Улучшенная генерация Part 1 (v2 Clean)
Убирает мусорные формулировки типа "genuine appreciation", "deeply engaged"
Делает ответы более естественными и релевантными вопросу
"""

import random
from typing import Tuple
from improved_generation_v2 import extract_topic_improved, get_discourse_marker
from error_injection import inject_errors_by_subscores

# Запрещенные фразы для Part 1
FORBIDDEN_PHRASES = [
    "genuine appreciation",
    "deeply engaged",
    "fundamental aspect",
    "intellectual enrichment",
    "personal fulfillment",
    "cultivated over time",
    "source of inspiration",
]

def generate_part1_templates_clean(topic: str, question: str, overall: float) -> list:
    """Генерирует чистые шаблоны Part 1 без мусорных формулировок"""
    
    # Извлекаем ключевые слова из вопроса для релевантности
    question_words = set(question.lower().split())
    topic_words = set(topic.lower().split())
    
    if overall <= 4.0:
        return [
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
        opening = get_discourse_marker("opening")
        return [
            f"{opening} I do like {topic}. I think it is interesting and I enjoy it.",
            f"I really like {topic}. It makes me happy and I do it often.",
            f"Yes, I enjoy {topic}. It is one of my favorite things to do.",
            f"{opening} I like {topic} quite a bit. I think it is fun and I do it when I have time.",
            f"Actually, I really enjoy {topic}. It is something I like to do in my free time.",
            f"I guess I like {topic}. It is interesting and I think it is good for me.",
            f"To be honest, I do like {topic}. I find it enjoyable and I do it regularly.",
            f"Well, I'd say I like {topic}. It is nice activity and I enjoy doing it.",
        ]
    
    elif overall <= 6.0:
        opening = get_discourse_marker("opening")
        opinion = get_discourse_marker("opinion")
        return [
            f"Yes, I do enjoy {topic}. I find it quite relaxing and it helps me unwind after a busy day.",
            f"I really like {topic}. It's something I do regularly, especially on weekends when I have more free time.",
            f"Absolutely, I'm quite fond of {topic}. {opinion} it's a great way to spend my leisure time and I always look forward to it.",
            f"{opening} I'd say I really enjoy {topic}. I find it both interesting and relaxing, and it's become a regular part of my routine.",
            f"Actually, I'm quite interested in {topic}. {opinion} it's a wonderful way to relax and I try to make time for it whenever possible.",
            f"To be honest, I really like {topic}. It's something that brings me joy and helps me feel more balanced in my daily life.",
            f"I guess I'd say I enjoy {topic}. I find it quite engaging and it's definitely one of my preferred ways to spend free time.",
            f"Personally, I'm quite enthusiastic about {topic}. {opinion} it adds value to my life and I appreciate the opportunities it provides.",
        ]
    
    elif overall <= 7.0:
        opening = get_discourse_marker("opening")
        opinion = get_discourse_marker("opinion")
        return [
            f"Yes, I absolutely enjoy {topic}. I find it both stimulating and rewarding. It's become an important part of my daily routine.",
            f"I'm quite passionate about {topic}. I appreciate how it allows me to explore different perspectives and learn new things.",
            f"Definitely, I'm very enthusiastic about {topic}. It's something that brings me both relaxation and a sense of accomplishment.",
            f"{opening} I really value {topic}. It's something I've been doing for a while, and it continues to be both enjoyable and meaningful.",
            f"Actually, I'm very interested in {topic}. I find that it provides a good combination of challenge and enjoyment that keeps me motivated.",
            f"I'd say I'm quite passionate about {topic}. It's become an important part of how I live my life, and I find it both interesting and fulfilling.",
            f"To be honest, I have a strong connection with {topic}. {opinion} it's something that has grown in importance for me, and I value what it adds to my experiences.",
        ]
    
    else:
        opening = get_discourse_marker("opening")
        return [
            f"I really value {topic}. It's become an important part of how I approach life, and I find it both interesting and meaningful.",
            f"Absolutely, I'm very interested in {topic}. I find that it provides a good combination of challenge and enjoyment that keeps me motivated.",
            f"Yes, I'm quite passionate about {topic}. It's something I've been doing for a while, and it continues to be both enjoyable and meaningful.",
        ]

def generate_part1_answer_v2_clean(question: str, overall: float, fc: float, lr: float, gra: float, pr: float) -> Tuple[str, int]:
    """Улучшенная генерация Part 1 без мусорных формулировок"""
    topic = extract_topic_improved(question)
    
    # Длительность зависит от уровня
    if overall <= 4.5:
        duration = random.randint(8, 18)
    elif overall <= 6.5:
        duration = random.randint(12, 22)
    else:
        duration = random.randint(18, 28)
    
    # Выбираем шаблон
    templates = generate_part1_templates_clean(topic, question, overall)
    answer = random.choice(templates)
    
    # Проверяем, что нет запрещенных фраз
    answer_lower = answer.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in answer_lower:
            # Заменяем на более простой шаблон
            if overall <= 6.0:
                answer = f"I really like {topic}. It's something I enjoy and find interesting."
            else:
                answer = f"I'm quite passionate about {topic}. I find it both interesting and rewarding."
            break
    
    # Проверяем релевантность (хотя бы одно слово из вопроса должно быть в ответе)
    question_words = set(question.lower().split())
    answer_words = set(answer.lower().split())
    if not question_words.intersection(answer_words) and len(question_words) > 3:
        # Добавляем контекст из вопроса
        key_word = [w for w in question_words if len(w) > 4 and w not in ['what', 'when', 'where', 'which', 'would', 'could', 'should']]
        if key_word:
            answer = answer.replace(topic, f"{topic} ({key_word[0]})", 1)
    
    # Применяем error injection
    answer = inject_errors_by_subscores(answer, fc, lr, gra, pr)
    
    return answer, duration

