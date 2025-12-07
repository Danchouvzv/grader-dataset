#!/usr/bin/env python3
"""
Улучшенная генерация Part 3 с:
- Множественными структурными шаблонами (4 варианта)
- Тематическими словарями
- Более четкими различиями между близкими бэндами (5.5 vs 6.0)
"""

import csv
import random
import re
from datetime import datetime, timedelta
from generate_synthetic_expansion import round_to_half, generate_realistic_subbands, load_existing_data, get_next_ids
from error_injection import inject_errors_by_subscores
from improve_generation import determine_quality_flag

# Тематические словари
TOPIC_VOCABULARY = {
    'technology': {
        'words': ['artificial intelligence', 'digital devices', 'social media', 'online platforms', 
                 'automation', 'cybersecurity', 'data privacy', 'virtual communication'],
        'concepts': ['technological advancement', 'digital transformation', 'connectivity', 'innovation']
    },
    'environment': {
        'words': ['carbon footprint', 'renewable energy', 'recycling', 'sustainability', 
                 'climate change', 'pollution', 'conservation', 'eco-friendly'],
        'concepts': ['environmental protection', 'green initiatives', 'sustainable living']
    },
    'education': {
        'words': ['online learning', 'traditional classrooms', 'academic performance', 
                 'educational system', 'curriculum', 'teaching methods', 'student engagement'],
        'concepts': ['educational opportunities', 'learning outcomes', 'academic achievement']
    },
    'society': {
        'words': ['social inequality', 'community', 'urbanization', 'aging population',
                 'social cohesion', 'public services', 'infrastructure', 'demographics'],
        'concepts': ['social dynamics', 'community development', 'social welfare']
    },
    'work': {
        'words': ['remote work', 'job satisfaction', 'career development', 'work-life balance',
                 'automation', 'employment opportunities', 'professional growth', 'workplace'],
        'concepts': ['employment trends', 'career progression', 'workplace dynamics']
    },
    'culture': {
        'words': ['cultural diversity', 'traditional values', 'cultural heritage', 'tourism',
                 'cultural exchange', 'local customs', 'cultural identity', 'globalization'],
        'concepts': ['cultural preservation', 'cultural integration', 'cross-cultural understanding']
    },
    'family': {
        'words': ['family structure', 'parenting', 'generational differences', 'family bonds',
                 'family relationships', 'family values', 'extended family', 'nuclear family'],
        'concepts': ['family dynamics', 'intergenerational relationships', 'family support']
    },
    'health': {
        'words': ['mental health', 'wellbeing', 'healthcare system', 'public health',
                 'preventive care', 'health awareness', 'lifestyle choices', 'health services'],
        'concepts': ['health outcomes', 'healthcare access', 'public health initiatives']
    }
}

def extract_topic_from_question(question: str) -> str:
    """Извлекает тему из вопроса для выбора словаря"""
    question_lower = question.lower()
    
    # Определяем тему по ключевым словам
    if any(word in question_lower for word in ['technology', 'artificial intelligence', 'ai', 'social media', 'digital', 'online']):
        return 'technology'
    elif any(word in question_lower for word in ['environment', 'climate', 'pollution', 'recycling', 'sustainable', 'green']):
        return 'environment'
    elif any(word in question_lower for word in ['education', 'school', 'university', 'teacher', 'student', 'learning']):
        return 'education'
    elif any(word in question_lower for word in ['society', 'community', 'social', 'inequality', 'urban', 'city']):
        return 'society'
    elif any(word in question_lower for word in ['work', 'job', 'career', 'employment', 'workplace', 'remote']):
        return 'work'
    elif any(word in question_lower for word in ['culture', 'cultural', 'tradition', 'heritage', 'tourism']):
        return 'culture'
    elif any(word in question_lower for word in ['family', 'parent', 'children', 'generation']):
        return 'family'
    elif any(word in question_lower for word in ['health', 'mental health', 'wellbeing', 'healthcare']):
        return 'health'
    else:
        return 'society'  # default

def get_topic_words(topic: str, count: int = 2) -> list:
    """Получает тематические слова"""
    vocab = TOPIC_VOCABULARY.get(topic, TOPIC_VOCABULARY['society'])
    words = vocab['words'] + vocab['concepts']
    return random.sample(words, min(count, len(words)))

def generate_part3_structure_v2(overall: float, topic: str) -> dict:
    """Генерирует структуру Part 3 с 4 вариантами"""
    
    topic_words = get_topic_words(topic, 2)
    word1, word2 = topic_words[0], topic_words[1] if len(topic_words) > 1 else topic_words[0]
    
    structures = {
        'structure_1': [],  # Benefits first, then challenges
        'structure_2': [],  # Challenges first, then benefits
        'structure_3': [],  # Examples/cases focused
        'structure_4': []   # Policy/individual level focus
    }
    
    if overall <= 4.0:
        structures['structure_1'] = [
            f"I think... it is important. Many people... they think about {word1}. It is good... but also... there are problems. I think we need to... do something. It is difficult question."
        ]
        structures['structure_2'] = [
            f"This is... um... complex question. I think... there are problems with {word1}. But also... there are good things. I think... we need solution."
        ]
        structures['structure_3'] = [
            f"Well... I think this is... important topic. Many people... they worry about {word1}. I think... we should... do something. But it is difficult."
        ]
        structures['structure_4'] = [
            f"To be honest... I think this is... complex. There are... good things... and bad things about {word1}. I don't know... what is best solution."
        ]
    
    elif overall <= 5.0:
        structures['structure_1'] = [
            f"I think this is complex question. On one hand, there are good things about {word1}. For example, it helps people and makes life better. But on other hand, there are problems too. People worry about this. I think we need to find balance. It is not easy, but I think it is possible.",
            f"I think {word1} is important topic. There are benefits - it can help people. But there are also challenges. I think we need to think carefully about this. It is not simple question."
        ]
        structures['structure_2'] = [
            f"I think there are problems with {word1}. For example, it can cause issues for some people. But I also think there are good things. It can help in some ways. I think we need to be careful and find good solution.",
            f"This is difficult question. I think {word1} has problems. But I also think it has benefits. We need to think about both sides. I think balance is important."
        ]
        structures['structure_3'] = [
            f"I can think of examples. Some people use {word1} and it helps them. But other people have problems with it. I think it depends on situation. Different people, different results.",
            f"I know people who use {word1}. Some are happy, some are not. I think it depends on how you use it. There is no one answer for everyone."
        ]
        structures['structure_4'] = [
            f"I think individuals can do something about {word1}. People can make choices. But also government or society should help. I think both levels are important. We need individual action and also support from society.",
            f"I think this is question for both people and government. Individuals can help with {word1}. But also we need rules and support. I think we need both approaches."
        ]
    
    elif overall <= 5.5:
        # 5.5: больше повторов, проще лексика, чуть более messy структура
        structures['structure_1'] = [
            f"I think this is complex issue. There are good things about {word1}. It can help people. It can make things better. But there are also problems. It can cause issues. I think we need to find balance. We need to think about good things and bad things. It is not easy, but I think it is possible to find solution.",
            f"I think {word1} is important. There are benefits. For example, it helps people. It makes life easier. But there are challenges too. Some people have problems. I think we need to be careful. We need to think about both sides. I think balance is important."
        ]
        structures['structure_2'] = [
            f"I think there are problems with {word1}. It can cause issues. Some people have difficulties. But I also think there are good things. It can help in some ways. It can be useful. I think we need to think about problems and benefits. We need to find way to reduce problems and keep benefits.",
            f"This is difficult question about {word1}. I think there are challenges. It can be problematic. But I also think it has benefits. It can help people. I think we need to consider both. We need balanced approach."
        ]
        structures['structure_3'] = [
            f"I can think of examples with {word1}. Some people use it and it helps them. They are happy. But other people have problems. They struggle. I think it depends on situation. Different people, different experiences. I think we need to understand this.",
            f"I know people who use {word1}. Some are successful. Some are not. I think it depends on how you use it. It depends on your situation. There is no one answer. Different people need different approaches."
        ]
        structures['structure_4'] = [
            f"I think individuals can do something about {word1}. People can make choices. They can change their behavior. But also government should help. Society should support. I think both are important. We need individual action. We also need support from society. Both levels matter.",
            f"I think this is question for both people and government. Individuals can help with {word1}. They can take action. But also we need rules. We need support from government. I think we need both. Individual effort and government support."
        ]
    
    elif overall <= 6.0:
        # 6.0: меньше мусора, больше логических связок
        structures['structure_1'] = [
            f"I think this is a complex issue that has multiple aspects. On one hand, {word1} offers clear benefits - it can improve efficiency and create opportunities. However, there are also significant challenges, such as potential negative impacts. I believe the key is finding a balanced approach. This requires careful consideration of different perspectives. Ultimately, I think it's about making informed decisions.",
            f"I think {word1} is a multifaceted topic. There are clear advantages - it can enhance quality of life and provide new opportunities. On the other hand, we must acknowledge potential drawbacks. I think the most effective solution involves considering both benefits and challenges. This means understanding different viewpoints and finding middle ground."
        ]
        structures['structure_2'] = [
            f"I think there are significant challenges with {word1}. It can create problems for certain groups and lead to unintended consequences. However, I also recognize that there are benefits. It can improve efficiency and offer new possibilities. I think the solution requires addressing the challenges while preserving the benefits. This means developing strategies that minimize harm and maximize positive outcomes.",
            f"This is a complex issue regarding {word1}. While there are clear problems that need attention, I also see potential benefits. I think the most effective approach involves recognizing both sides and finding solutions that address concerns while maintaining advantages. This requires thoughtful planning and consideration of various factors."
        ]
        structures['structure_3'] = [
            f"I can think of several examples related to {word1}. In some cases, it has proven very beneficial - people have experienced positive outcomes and improved situations. However, in other instances, it has created difficulties. I think the key is understanding that results vary depending on context and individual circumstances. This means we need flexible approaches that can adapt to different situations.",
            f"Looking at real examples of {word1}, I see varied outcomes. Some people have had very positive experiences, while others have faced challenges. I think this variation shows that success depends on multiple factors - how it's implemented, the specific context, and individual needs. I believe we need approaches that can accommodate this diversity."
        ]
        structures['structure_4'] = [
            f"I think addressing {word1} requires action at multiple levels. On an individual level, people can make informed choices and adapt their behavior. At the same time, government and institutions play a crucial role in creating supportive frameworks. I think the most effective solutions combine individual responsibility with systemic support. This means both personal action and policy measures are necessary.",
            f"I think {word1} is an issue that needs both individual and collective responses. People can contribute through their choices and actions. However, I also believe that government and organizations should provide guidance and support. I think successful solutions require coordination between personal efforts and institutional frameworks."
        ]
    
    elif overall <= 7.0:
        structures['structure_1'] = [
            f"This is a multifaceted issue that requires careful consideration of various factors. On one hand, {word1} offers compelling benefits - increased efficiency, enhanced opportunities, and improved quality of life for many. However, we must also acknowledge potential drawbacks, including unintended consequences and challenges to existing systems. I think the most effective approach involves recognizing that this isn't a binary choice, but rather requires nuanced solutions that can adapt to different contexts. This means considering perspectives of various stakeholders and understanding long-term implications.",
            f"I think {word1} represents a complex challenge with multiple dimensions. There are undeniable advantages - it can drive innovation, expand access, and create new possibilities. At the same time, we must be mindful of potential negative effects, such as unequal distribution of benefits or disruption to established practices. I believe the solution lies in developing flexible frameworks that can balance competing interests and adapt to changing circumstances."
        ]
        structures['structure_2'] = [
            f"I think there are serious concerns regarding {word1} that cannot be ignored. It can lead to unintended consequences, create inequalities, and disrupt existing structures. However, I also recognize that it offers significant potential benefits - improved efficiency, expanded opportunities, and enhanced capabilities. I think the challenge is developing approaches that can mitigate risks while harnessing advantages. This requires careful analysis, stakeholder engagement, and willingness to adjust strategies based on evidence.",
            f"While {word1} presents substantial challenges - including potential negative impacts on certain groups and questions about long-term sustainability - I also see considerable benefits. It can increase productivity, create new opportunities, and address existing limitations. I think the most promising path forward involves creating mechanisms that can identify and address problems early while maximizing positive outcomes."
        ]
        structures['structure_3'] = [
            f"Examining concrete examples of {word1}, I see a pattern of varied outcomes. In successful cases, it has led to significant improvements - better results, increased satisfaction, and positive transformations. However, there are also instances where it has created difficulties or failed to deliver expected benefits. I think this variation highlights the importance of context-specific approaches. The key is understanding what factors contribute to success and developing strategies that can be adapted to different situations.",
            f"Looking at real-world applications of {word1}, the results are mixed. Some implementations have been highly successful, demonstrating clear benefits and positive impacts. Others have encountered obstacles or produced unintended consequences. I think this diversity of outcomes suggests that success depends on multiple factors - proper planning, adequate resources, stakeholder buy-in, and ability to adapt. I believe we need approaches that can learn from both successes and failures."
        ]
        structures['structure_4'] = [
            f"I think addressing {word1} effectively requires coordinated action across multiple levels. At the individual level, people can make informed decisions and adapt their practices. However, I also believe that institutional and policy frameworks are essential - they can create enabling conditions, provide resources, and ensure equitable access. I think the most effective solutions emerge when individual agency is supported by systemic structures. This means policies that empower people while providing necessary safeguards and support.",
            f"I think {word1} is an issue that demands both bottom-up and top-down approaches. Individual actions matter - people can make choices that align with their values and circumstances. At the same time, I believe that government and organizations have crucial roles in creating frameworks, providing resources, and ensuring fairness. I think successful solutions require alignment between personal initiatives and institutional support."
        ]
    
    else:
        structures['structure_1'] = [
            f"This represents one of the most pressing and complex challenges of our time, requiring us to navigate multiple competing priorities and perspectives. On one hand, {word1} offers undeniable benefits - the potential for increased efficiency, expanded opportunities, and enhanced quality of life. However, we must also grapple with significant concerns, including potential unintended consequences, questions of equity and access, and the ways in which rapid change can disrupt existing social and economic structures. I think the fundamental challenge is recognizing that simplistic solutions are inadequate - we need approaches that can accommodate complexity, adapt to changing circumstances, and balance multiple legitimate interests. This requires not just technical solutions, but also thoughtful consideration of ethical implications, long-term sustainability, and the ways in which different groups will be affected.",
            f"I think {word1} embodies a fundamental tension in contemporary society - the need to balance innovation and progress with careful consideration of consequences. There are compelling arguments for its benefits, including transformative potential and ability to address longstanding challenges. Simultaneously, we must acknowledge serious concerns about equity, sustainability, and potential disruption. I believe the most promising path forward involves creating adaptive frameworks that can evolve, incorporating diverse perspectives, and maintaining commitment to both innovation and responsibility."
        ]
        structures['structure_2'] = [
            f"While {word1} presents substantial challenges that demand serious attention - including questions of equity, sustainability, and potential unintended consequences - I also recognize its transformative potential. The benefits can be significant: increased efficiency, expanded opportunities, and ability to address complex problems. I think the key is developing sophisticated approaches that can simultaneously address concerns while maximizing benefits. This requires deep understanding of underlying dynamics, engagement with diverse stakeholders, and creation of mechanisms that can adapt and learn.",
            f"I think {word1} raises profound questions about how we navigate change in complex systems. The challenges are real and significant - they include potential negative impacts on vulnerable groups, questions about long-term sustainability, and risks of unintended consequences. However, I also see considerable potential for positive transformation. I believe the solution lies in developing nuanced, adaptive approaches that can balance competing priorities, incorporate multiple perspectives, and evolve based on evidence and experience."
        ]
        structures['structure_3'] = [
            f"Examining {word1} through lens of concrete examples reveals both remarkable successes and significant challenges. In cases where conditions were favorable, it has produced transformative outcomes - substantial improvements, innovative solutions, and positive change. However, there are also instances where implementation has encountered obstacles or produced mixed results. I think this variation underscores the importance of context-specific understanding. The challenge is developing approaches that can identify key success factors, adapt to different circumstances, and learn systematically from both achievements and setbacks.",
            f"Looking at empirical evidence regarding {word1}, the picture is complex. Some applications have demonstrated exceptional results, showing clear benefits and positive impacts across multiple dimensions. Others have revealed limitations, challenges, or unintended consequences. I think this complexity highlights the need for sophisticated, context-aware approaches. Success depends on understanding underlying mechanisms, recognizing contextual factors, and developing strategies that can be refined based on experience and evidence."
        ]
        structures['structure_4'] = [
            f"I think addressing {word1} effectively requires sophisticated understanding of how individual actions and systemic structures interact. At the individual level, people can make informed choices, adapt their practices, and contribute to positive outcomes. However, I also believe that institutional frameworks are crucial - they can create enabling conditions, ensure equitable access, and provide necessary safeguards. I think the most effective solutions emerge when individual agency is supported by well-designed systemic structures. This means policies and institutions that empower people while providing frameworks for coordination, resource allocation, and protection of collective interests.",
            f"I think {word1} demands integrated approaches that recognize interdependence between individual and collective levels. Personal actions matter - people can make choices that reflect their values and contribute to desired outcomes. Simultaneously, I believe that government, organizations, and institutions play essential roles in creating frameworks, providing resources, and ensuring fairness. I think successful solutions require careful coordination between bottom-up initiatives and top-down structures, with mechanisms for feedback, adaptation, and alignment of interests."
        ]
    
    return structures

def generate_part3_answer_v2(question: str, overall: float, fc: float, lr: float, gra: float, pr: float) -> tuple:
    """Улучшенная генерация Part 3 с множественными шаблонами"""
    duration = random.randint(35, 65)
    
    # Длительность зависит от уровня
    if overall <= 4.5:
        duration = random.randint(25, 45)
    elif overall <= 6.5:
        duration = random.randint(40, 60)
    else:
        duration = random.randint(50, 75)
    
    # Извлекаем тему
    topic = extract_topic_from_question(question)
    
    # Получаем структуры
    structures = generate_part3_structure_v2(overall, topic)
    
    # Выбираем случайную структуру
    structure_key = random.choice(list(structures.keys()))
    templates = structures[structure_key]
    
    if templates:
        answer = random.choice(templates)
    else:
        # Fallback
        answer = f"I think this is a complex issue. There are benefits and challenges. I think we need balanced approach."
    
    # Применяем Error Injection
    answer = inject_errors_by_subscores(answer, fc, lr, gra, pr)
    
    return answer, duration

def generate_part3_questions() -> list:
    """Генерирует вопросы для Part 3"""
    # Используем ту же функцию из оригинального файла
    from generate_part3_expansion import generate_part3_questions as orig_func
    return orig_func()

# Для обратной совместимости
def generate_part3_answer(question: str, overall: float, fc: float, lr: float, gra: float, pr: float) -> tuple:
    return generate_part3_answer_v2(question, overall, fc, lr, gra, pr)

