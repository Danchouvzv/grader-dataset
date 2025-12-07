#!/usr/bin/env python3
"""
Улучшенная генерация v2.0 с:
- 5-8 шаблонов на диапазон
- Дискурсивные маркеры и коннекторы
- Разная структура (вступление, развитие, рефлексия)
- Привязка ошибок к субскорам через error_injection
"""

import random
import re
from typing import List, Tuple, Dict
from error_injection import inject_errors_by_subscores

# Дискурсивные маркеры и коннекторы
DISCOURSE_MARKERS = {
    "opening": [
        "Well,", "Actually,", "To be honest,", "I'd say that", "From my perspective,",
        "In my opinion,", "Personally,", "I suppose", "I guess", "To some extent,",
    ],
    "contrast": [
        "however", "on the other hand", "but at the same time", "although",
        "despite this", "nevertheless", "yet",
    ],
    "addition": [
        "in addition", "moreover", "also", "furthermore", "what's more",
        "besides", "additionally",
    ],
    "opinion": [
        "I think", "I believe", "I feel", "in my view", "from my point of view",
        "it seems to me", "I'd argue that",
    ],
    "reflection": [
        "looking back", "in retrospect", "I realize that", "it taught me that",
        "this experience showed me", "I learned that",
    ]
}

def extract_topic_improved(question: str) -> str:
    """Улучшенное извлечение темы с fallback"""
    question_lower = question.lower()
    
    # Специфичные паттерны
    patterns = [
        # Захватываем с артиклем
        (r'describe ((?:a|an) .+?)(?: you| that| which| who|$)', lambda m: m.group(1)),
        (r'(?:like|enjoy)\s+(.+?)\?', lambda m: re.sub(r'\b(do|you|to|the|a|an)\b', '', m.group(1)).strip()),
        (r'what kind of (\w+)', lambda m: m.group(1)),
        (r'how often do you (.+?)\?', lambda m: re.sub(r'\buse\b', '', m.group(1)).strip()),
        (r'(?:what\'s|what is) your (.+?)\?', lambda m: re.sub(r'\bfavorite\b', '', m.group(1)).strip()),
        (r'how do you (.+?)\?', lambda m: m.group(1) + 'ing' if not m.group(1).endswith('ing') else m.group(1)),
    ]
    
    for pattern, processor in patterns:
        match = re.search(pattern, question_lower)
        if match:
            result = processor(match)
            if result:
                return result
    
    # Fallback
    words = question.split()
    if words:
        return words[-1].rstrip('?')
    return "it"

def get_discourse_marker(category: str) -> str:
    """Получает случайный дискурсивный маркер"""
    markers = DISCOURSE_MARKERS.get(category, [])
    return random.choice(markers) if markers else ""

def generate_part1_templates_v2(topic: str, overall: float) -> List[str]:
    """Генерирует 5-8 шаблонов для Part 1 в зависимости от уровня"""
    
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
            f"Actually, I'm quite passionate about {topic}. {opinion} it's a wonderful way to relax and I try to make time for it whenever possible.",
            f"To be honest, I really like {topic}. It's something that brings me joy and helps me feel more balanced in my daily life.",
            f"I guess I'd say I enjoy {topic}. I find it quite engaging and it's definitely one of my preferred ways to spend free time.",
            f"Personally, I'm quite enthusiastic about {topic}. {opinion} it adds value to my life and I appreciate the opportunities it provides.",
        ]
    
    elif overall <= 7.0:
        opening = get_discourse_marker("opening")
        opinion = get_discourse_marker("opinion")
        return [
            f"Yes, I absolutely enjoy {topic}. I find it both intellectually stimulating and personally rewarding. It's become an integral part of my daily routine.",
            f"I'm quite passionate about {topic}. I appreciate how it allows me to explore different perspectives and continuously learn new things.",
            f"Definitely, I'm very enthusiastic about {topic}. It's something that brings me both relaxation and a sense of accomplishment.",
            f"{opening} I have a genuine appreciation for {topic}. It's something I've cultivated over time, and it continues to be a source of both inspiration and satisfaction.",
            f"Actually, I'm deeply engaged with {topic}. I find that it provides a unique combination of challenge and enjoyment that keeps me motivated.",
            f"I'd say I'm quite passionate about {topic}. It's become a fundamental aspect of how I approach life, offering both intellectual enrichment and personal fulfillment.",
            f"To be honest, I have a real connection with {topic}. {opinion} it's something that has grown in importance for me over the years, and I value the depth it adds to my experiences.",
        ]
    
    else:
        opening = get_discourse_marker("opening")
        return [
            f"I have a genuine appreciation for {topic}. It's become a fundamental aspect of how I approach life, offering both intellectual enrichment and personal fulfillment.",
            f"Absolutely, I'm deeply engaged with {topic}. I find that it provides a unique combination of challenge and enjoyment that keeps me motivated.",
            f"Yes, I'm quite passionate about {topic}. It's something I've cultivated over time, and it continues to be a source of both inspiration and satisfaction.",
        ]

def generate_part1_answer_v2(question: str, overall: float, fc: float, lr: float, gra: float, pr: float) -> Tuple[str, int]:
    """Улучшенная генерация Part 1 с вариативностью и привязкой к субскорам"""
    topic = extract_topic_improved(question)
    
    # Длительность зависит от уровня
    if overall <= 4.5:
        duration = random.randint(8, 18)
    elif overall <= 6.5:
        duration = random.randint(12, 22)
    else:
        duration = random.randint(18, 28)
    
    # Выбираем шаблон
    templates = generate_part1_templates_v2(topic, overall)
    answer = random.choice(templates)
    
    # Применяем error injection в зависимости от субскоров
    answer = inject_errors_by_subscores(answer, fc, lr, gra, pr)
    
    return answer, duration

def generate_part2_structure_v2(overall: float) -> Dict[str, List[str]]:
    """Генерирует структуру Part 2 с разными вариантами"""
    
    structures = {
        "introduction": [],
        "background": [],
        "main_body": [],
        "reflection": [],
    }
    
    if overall <= 4.0:
        structures["introduction"] = [
            "I want to talk about ...",
            "I like to describe ...",
            "I want to say about ...",
        ]
        structures["main_body"] = [
            "It was... good. I like it. It was... nice.",
            "I remember... it was last year. I was happy.",
        ]
        structures["reflection"] = [
            "It was good experience.",
            "I like it very much.",
        ]
    
    elif overall <= 5.0:
        structures["introduction"] = [
            "I'd like to describe ...",
            "I want to talk about ...",
            "I'd like to tell you about ...",
        ]
        structures["background"] = [
            "It happened last year.",
            "This was about two years ago.",
        ]
        structures["main_body"] = [
            "I remember it was very interesting. I enjoyed it a lot.",
            "What I liked most was that it was fun and I had good time.",
        ]
        structures["reflection"] = [
            "I think it was important experience for me.",
            "I learned something from it.",
        ]
    
    elif overall <= 6.0:
        opening = get_discourse_marker("opening")
        structures["introduction"] = [
            f"I'd like to talk about ...",
            f"{opening} I want to describe ...",
            f"I'd like to tell you about ...",
        ]
        structures["background"] = [
            "This was something that happened about a year ago.",
            "It occurred approximately two years ago.",
        ]
        structures["main_body"] = [
            "What made it particularly memorable was the way it challenged my expectations.",
            "I remember feeling both excited and a bit nervous at first.",
            "As things progressed, I found myself really enjoying the experience.",
        ]
        structures["reflection"] = [
            "Looking back, I realize this experience has influenced how I approach similar situations today.",
            "This experience taught me something valuable about myself and my capabilities.",
        ]
    
    elif overall <= 7.0:
        opening = get_discourse_marker("opening")
        reflection = get_discourse_marker("reflection")
        structures["introduction"] = [
            f"I'd like to describe ..., which has been a significant experience in my life.",
            f"{opening} I want to talk about ..., which fundamentally changed how I understand certain aspects of life.",
        ]
        structures["background"] = [
            "This occurred approximately two years ago, and it fundamentally changed how I understand certain aspects of life.",
            "It happened about three years ago, during a period when I was exploring new opportunities.",
        ]
        structures["main_body"] = [
            "What made it particularly meaningful was the combination of challenge and growth it presented.",
            "I remember the initial period was quite demanding, requiring me to step outside my comfort zone.",
            "However, as I navigated through the experience, I discovered strengths and capabilities I hadn't recognized before.",
        ]
        structures["reflection"] = [
            f"{reflection} it taught me about resilience, adaptability, and the importance of maintaining perspective during difficult times.",
            "This experience continues to influence my decisions and approach to new challenges.",
        ]
    
    else:
        opening = get_discourse_marker("opening")
        reflection = get_discourse_marker("reflection")
        structures["introduction"] = [
            f"I'd like to describe ..., which represents one of the most transformative experiences I've had.",
        ]
        structures["background"] = [
            "This occurred about three years ago, and it fundamentally reshaped my understanding of both myself and the world around me.",
        ]
        structures["main_body"] = [
            "What made it particularly profound was the way it combined intellectual challenge with emotional growth.",
            "I remember the initial phase was quite intense, as I had to confront assumptions I'd held for years.",
            "However, as I immersed myself in the experience, I began to appreciate its transformative potential.",
        ]
        structures["reflection"] = [
            f"{reflection} it taught me about the importance of intellectual humility and the value of sustained effort.",
            "This experience has become a touchstone for how I approach learning, growth, and engagement with complex issues.",
        ]
    
    return structures

def generate_part2_answer_v2(question: str, overall: float, fc: float, lr: float, gra: float, pr: float) -> Tuple[str, int]:
    """Генерирует улучшенный ответ Part 2 с структурой"""
    topic = extract_topic_improved(question)
    
    # Длительность зависит от уровня
    if overall <= 4.5:
        duration = random.randint(30, 45)
    elif overall <= 6.5:
        duration = random.randint(45, 60)
    else:
        duration = random.randint(55, 70)
    
    # Получаем структуру
    structure = generate_part2_structure_v2(overall)
    
    # Собираем ответ из частей
    parts = []
    
    if structure["introduction"]:
        intro = random.choice(structure["introduction"])
        # Правильная подстановка темы
        if "..." in intro:
            intro = intro.replace(" ...", " " + topic).replace("...", topic)
        parts.append(intro)
    
    if structure["background"] and random.random() < 0.7:
        parts.append(random.choice(structure["background"]))
    
    if structure["main_body"]:
        # Добавляем 2-4 пункта main body
        main_points = random.sample(structure["main_body"], min(len(structure["main_body"]), random.randint(2, 4)))
        parts.extend(main_points)
    
    if structure["reflection"] and random.random() < 0.8:
        parts.append(random.choice(structure["reflection"]))
    
    answer = " ".join(parts)
    
    # Применяем error injection
    answer = inject_errors_by_subscores(answer, fc, lr, gra, pr)
    
    return answer, duration

def main():
    """Тестирование улучшенной генерации v2"""
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ ГЕНЕРАЦИИ V2")
    print("=" * 70)
    
    test_questions = [
        "Do you like listening to music?",
        "How often do you use social media?",
        "Describe a place you visited.",
    ]
    
    test_cases = [
        (4.0, 4.0, 3.5, 4.0, 4.5),
        (5.5, 5.5, 4.5, 6.0, 5.5),
        (6.0, 6.5, 5.5, 7.0, 6.0),
        (7.0, 7.5, 8.0, 6.5, 7.0),
    ]
    
    for question in test_questions[:2]:  # Part 1 вопросы
        print(f"\n📝 Part 1 - Вопрос: {question}")
        for overall, fc, lr, gra, pr in test_cases:
            answer, duration = generate_part1_answer_v2(question, overall, fc, lr, gra, pr)
            print(f"\n   Overall={overall}, FC={fc}, LR={lr}, GRA={gra}, PR={pr}")
            print(f"   Ответ: {answer}")
            print(f"   Длительность: {duration} сек")
    
    # Part 2
    print(f"\n📝 Part 2 - Вопрос: {test_questions[2]}")
    for overall, fc, lr, gra, pr in test_cases:
        answer, duration = generate_part2_answer_v2(test_questions[2], overall, fc, lr, gra, pr)
        print(f"\n   Overall={overall}, FC={fc}, LR={lr}, GRA={gra}, PR={pr}")
        print(f"   Ответ: {answer[:150]}...")
        print(f"   Длительность: {duration} сек")

if __name__ == '__main__':
    main()

