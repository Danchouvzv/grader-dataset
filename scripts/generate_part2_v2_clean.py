#!/usr/bin/env python3
"""
Улучшенная генерация Part 2 (v2 Clean)
Убирает шаблонные фразы типа "I'd like to describe time when you"
Исправляет неестественную длину
"""

import random
from typing import Tuple, Dict, List
from improved_generation_v2 import extract_topic_improved, get_discourse_marker
from error_injection import inject_errors_by_subscores

# Запрещенные шаблонные фразы для Part 2
FORBIDDEN_PHRASES = [
    "I'd like to describe time when you",
    "This was something that happened about a year ago",
    "What made it particularly memorable",
    "challenged my expectations",
    "opened up new perspectives",
]

def generate_part2_structure_clean(overall: float, topic: str) -> Dict[str, List[str]]:
    """Генерирует чистую структуру Part 2 без шаблонности"""
    
    structures = {
        "introduction": [],
        "background": [],
        "main_body": [],
        "reflection": []
    }
    
    if overall <= 4.0:
        structures["introduction"] = [
            f"I want to talk about {topic}.",
            f"I like to describe {topic}.",
            f"I want to say about {topic}.",
        ]
        structures["background"] = [
            "It was last year.",
            "It happened when I was student.",
            "I remember it was long time ago.",
        ]
        structures["main_body"] = [
            "It was good. I like it very much.",
            "It was interesting. I enjoyed it.",
            "It was nice experience. I was happy.",
        ]
        structures["reflection"] = [
            "I think it was good.",
            "I remember it was nice.",
        ]
    
    elif overall <= 5.0:
        structures["introduction"] = [
            f"I'd like to tell you about {topic}.",
            f"I want to talk about {topic}.",
            f"Let me describe {topic}.",
        ]
        structures["background"] = [
            "This happened about a year ago.",
            "It was when I was studying at university.",
            "I remember this was during my summer break.",
        ]
        structures["main_body"] = [
            "What I remember most was that it was very interesting.",
            "I enjoyed it a lot because it was fun and exciting.",
            "The best part was that I learned something new.",
            "I think what made it special was that it was different from usual.",
        ]
        structures["reflection"] = [
            "Looking back, I think it was important experience for me.",
            "I learned something from it and I'm glad it happened.",
        ]
    
    elif overall <= 6.0:
        opening = get_discourse_marker("opening")
        structures["introduction"] = [
            f"I'd like to talk about {topic}.",
            f"{opening} I want to describe {topic}.",
            f"Let me tell you about {topic}.",
        ]
        structures["background"] = [
            "This happened about two years ago, and it left a strong impression on me.",
            "It was during my time at university, and I remember it quite clearly.",
            "I think this was about a year and a half ago, and it was quite memorable.",
        ]
        structures["main_body"] = [
            "What I remember most was how it challenged me in a good way.",
            "I really enjoyed it because it was both fun and educational.",
            "The best part was that I got to experience something completely new.",
            "What made it special was the way it changed my perspective on things.",
            "I think what stood out to me was how different it was from what I expected.",
        ]
        structures["reflection"] = [
            "Looking back, I realize this experience taught me something valuable.",
            "I think this was important because it helped me understand things better.",
            "This experience has influenced how I approach similar situations today.",
        ]
    
    elif overall <= 7.0:
        opening = get_discourse_marker("opening")
        structures["introduction"] = [
            f"I'd like to describe {topic}, which has been a significant experience in my life.",
            f"{opening} I want to talk about {topic}, which fundamentally changed how I understand certain things.",
        ]
        structures["background"] = [
            "This occurred approximately two years ago, and it had a profound impact on me.",
            "It was during a period when I was exploring new opportunities, and this experience stood out.",
        ]
        structures["main_body"] = [
            "What I remember most was how it required me to step outside my comfort zone.",
            "I really appreciated it because it combined challenge with opportunity for growth.",
            "The most significant aspect was discovering strengths I hadn't recognized before.",
            "What made it particularly meaningful was the way it connected with my personal values.",
            "I think what stood out was how it balanced difficulty with genuine enjoyment.",
        ]
        structures["reflection"] = [
            "Looking back, I realize this experience taught me about resilience and adaptability.",
            "This has become important to me because it showed me new ways of thinking.",
            "This experience continues to influence my decisions and approach to new challenges.",
        ]
    
    else:
        opening = get_discourse_marker("opening")
        structures["introduction"] = [
            f"I'd like to describe {topic}, which represents one of the most meaningful experiences I've had.",
        ]
        structures["background"] = [
            "This occurred about three years ago, and it fundamentally reshaped my understanding.",
        ]
        structures["main_body"] = [
            "What I remember most was how it combined intellectual challenge with personal growth.",
            "I really valued it because it required me to engage deeply with complex questions.",
            "The most significant aspect was discovering new perspectives I hadn't considered before.",
            "What made it particularly profound was the way it connected different aspects of my life.",
            "I think what stood out was how it balanced challenge with genuine opportunity for development.",
        ]
        structures["reflection"] = [
            "Looking back, I realize this experience taught me about the importance of intellectual humility and sustained effort.",
            "This has become a touchstone for how I approach learning, growth, and engagement with complex issues.",
        ]
    
    return structures

def generate_part2_answer_v2_clean(question: str, overall: float, fc: float, lr: float, gra: float, pr: float) -> Tuple[str, int]:
    """Генерирует улучшенный ответ Part 2 без шаблонности"""
    topic = extract_topic_improved(question)
    
    # Длительность зависит от уровня (Part 2 должен быть длинным!)
    if overall <= 4.5:
        duration = random.randint(40, 55)
    elif overall <= 6.5:
        duration = random.randint(50, 65)
    else:
        duration = random.randint(60, 75)
    
    # Получаем структуру
    structure = generate_part2_structure_clean(overall, topic)
    
    # Собираем ответ из частей
    parts = []
    
    if structure["introduction"]:
        intro = random.choice(structure["introduction"])
        parts.append(intro)
    
    if structure["background"] and random.random() < 0.7:
        parts.append(random.choice(structure["background"]))
    
    if structure["main_body"]:
        # Добавляем 3-5 пунктов main body для достаточной длины
        num_points = random.randint(3, 5) if overall >= 6.0 else random.randint(2, 4)
        main_points = random.sample(structure["main_body"], min(len(structure["main_body"]), num_points))
        parts.extend(main_points)
    
    if structure["reflection"] and random.random() < 0.8:
        parts.append(random.choice(structure["reflection"]))
    
    answer = " ".join(parts)
    
    # Проверяем длину (Part 2 должен быть 100-180 слов)
    word_count = len(answer.split())
    if word_count < 80 and overall >= 6.0:
        # Добавляем еще один пункт
        if structure["main_body"]:
            extra = random.choice(structure["main_body"])
            if extra not in parts:
                parts.insert(-1, extra)
                answer = " ".join(parts)
    
    # Проверяем на запрещенные фразы
    answer_lower = answer.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in answer_lower:
            # Регенерируем с другим шаблоном
            if structure["introduction"]:
                intro = random.choice([i for i in structure["introduction"] if phrase.lower() not in i.lower()])
                if intro:
                    parts[0] = intro
                    answer = " ".join(parts)
    
    # Применяем error injection
    answer = inject_errors_by_subscores(answer, fc, lr, gra, pr)
    
    return answer, duration

