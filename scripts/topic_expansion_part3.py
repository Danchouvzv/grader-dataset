#!/usr/bin/env python3
"""
Topic Expansion для Part 3
Добавление 30-50 современных топиков для покрытия IELTS framework
"""

import csv
import random
from datetime import datetime, timedelta
from generate_synthetic_expansion import round_to_half, generate_realistic_subbands, load_existing_data, get_next_ids

def generate_modern_part3_topics() -> list:
    """Генерирует современные топики Part 3 (2024-2025)"""
    topics = [
        # Technology & AI
        ("q_part3_127", "How will artificial intelligence change education?"),
        ("q_part3_128", "Should AI be used to grade student work?"),
        ("q_part3_129", "What are the ethical concerns about AI?"),
        ("q_part3_130", "How has social media affected mental health?"),
        ("q_part3_131", "Should governments regulate social media platforms?"),
        ("q_part3_132", "How has remote work changed the workplace?"),
        
        # Education
        ("q_part3_133", "Can online education replace traditional schools?"),
        ("q_part3_134", "What role should teachers play in students' lives?"),
        ("q_part3_135", "Is university education necessary for success?"),
        ("q_part3_136", "How can we reduce pressure on students from exams?"),
        ("q_part3_137", "What is the value of lifelong learning?"),
        
        # Work & Life Balance
        ("q_part3_138", "How can young professionals balance work and personal life?"),
        ("q_part3_139", "What makes a job satisfying?"),
        ("q_part3_140", "Should people change careers frequently?"),
        ("q_part3_141", "How will automation affect future jobs?"),
        ("q_part3_142", "What skills will be important in the future?"),
        
        # Society & Migration
        ("q_part3_143", "Why do young people migrate to other countries?"),
        ("q_part3_144", "What are the challenges of an aging population?"),
        ("q_part3_145", "How can we reduce social inequality?"),
        ("q_part3_146", "What makes a strong community?"),
        ("q_part3_147", "How has urbanization changed society?"),
        ("q_part3_148", "What are the differences between city and rural life?"),
        
        # Environment & Sustainability
        ("q_part3_149", "What can individuals do to protect the environment?"),
        ("q_part3_150", "Should governments prioritize economic growth or environmental protection?"),
        ("q_part3_151", "How can we encourage sustainable living?"),
        ("q_part3_152", "What are the consequences of climate change?"),
        ("q_part3_153", "How can cities become more sustainable?"),
        ("q_part3_154", "What role should renewable energy play?"),
        
        # Culture & Globalization
        ("q_part3_155", "How does globalization affect local cultures?"),
        ("q_part3_156", "Should countries protect their local industries?"),
        ("q_part3_157", "How can we preserve traditional culture?"),
        ("q_part3_158", "What is the value of cultural diversity?"),
        ("q_part3_159", "How does tourism affect local culture?"),
        ("q_part3_160", "Should cultures change to adapt to modern times?"),
        
        # Psychology & Mental Health
        ("q_part3_161", "Why do people experience stress?"),
        ("q_part3_162", "How important is work-life balance?"),
        ("q_part3_163", "What factors motivate people?"),
        ("q_part3_164", "How can we improve mental health awareness?"),
        ("q_part3_165", "How has social media affected self-esteem?"),
        ("q_part3_166", "What causes digital addiction?"),
        
        # Family & Relationships
        ("q_part3_167", "How have family structures changed?"),
        ("q_part3_168", "What makes a good parent?"),
        ("q_part3_169", "How do generational differences affect relationships?"),
        ("q_part3_170", "What is the importance of family in modern society?"),
        ("q_part3_171", "How has technology affected family relationships?"),
        
        # Economics & Entrepreneurship
        ("q_part3_172", "How does consumerism affect society?"),
        ("q_part3_173", "What causes economic inequality?"),
        ("q_part3_174", "Should governments support small businesses?"),
        ("q_part3_175", "How important is entrepreneurship?"),
        ("q_part3_176", "What is financial literacy and why is it important?"),
        
        # Urbanization & City Life
        ("q_part3_177", "What are the challenges of city life?"),
        ("q_part3_178", "How can we improve urban planning?"),
        ("q_part3_179", "What attracts people to cities?"),
        ("q_part3_180", "How can cities solve traffic problems?"),
        ("q_part3_181", "What makes a city livable?"),
        
        # Ethics & Privacy
        ("q_part3_182", "How should we balance privacy and security?"),
        ("q_part3_183", "What are the ethical implications of AI?"),
        ("q_part3_184", "Should animal rights be protected?"),
        ("q_part3_185", "What are the ethical challenges in medicine?"),
        ("q_part3_186", "How should we handle fake news?"),
        
        # Arts & Society
        ("q_part3_187", "How does music influence society?"),
        ("q_part3_188", "What role should art play in education?"),
        ("q_part3_189", "How important is creativity in modern life?"),
        ("q_part3_190", "Should governments fund the arts?"),
        
        # Youth & Future
        ("q_part3_191", "What challenges do young people face today?"),
        ("q_part3_192", "How can we prepare young people for the future?"),
        ("q_part3_193", "What are the benefits and drawbacks of being young?"),
        ("q_part3_194", "How has childhood changed over the years?"),
    ]
    return topics

def generate_part3_answer_improved(question: str, overall: float, fc: float, lr: float, gra: float, pr: float) -> tuple:
    """Генерирует улучшенный ответ Part 3 с привязкой к субскорам"""
    duration = random.randint(35, 70)
    
    # Длительность зависит от уровня
    if overall <= 4.5:
        duration = random.randint(25, 45)
    elif overall <= 6.5:
        duration = random.randint(40, 60)
    else:
        duration = random.randint(50, 75)
    
    # Множество шаблонов для каждого диапазона
    if overall <= 4.0:
        templates = [
            "I think... it is important. Many people... they think about this. It is good... but also... there are problems. I think we need to... do something. It is difficult question.",
            "This is... um... complex question. I think... there are good things and bad things. It is not easy to say. I think we need... to find solution.",
            "Well... I think this is... important topic. Many people... they worry about this. I think... we should... do something. But it is difficult.",
            "To be honest... I think this is... complex. There are... good things... and bad things. I don't know... what is best solution.",
        ]
        
    elif overall <= 5.0:
        templates = [
            "I think this is complex question. On one hand, there are good things. For example, it helps people and makes life better. But on other hand, there are problems too. People worry about this. I think we need to find balance. It is not easy, but I think it is possible.",
            "Well, I think this issue has two sides. First, there are benefits - it can help people and improve things. However, there are also negative aspects that we need to consider. I believe the key is finding middle way that works for everyone.",
            "Actually, I think this is difficult topic. There are advantages and disadvantages. On positive side, it can bring improvements. But there are also concerns that people have. I think we need to think carefully about this.",
        ]
        
    elif overall <= 6.0:
        templates = [
            "I think this is a complex issue that has multiple aspects. On one hand, there are clear benefits - it can improve efficiency, create opportunities, and enhance quality of life. However, there are also significant challenges, such as potential negative impacts on certain groups or unintended consequences. I believe the key is finding a balanced approach that maximizes benefits while minimizing harm. This requires careful consideration of different perspectives and long-term implications. Ultimately, I think it's about making informed decisions rather than simply accepting or rejecting change.",
            "This is definitely a multifaceted question that doesn't have a simple answer. I think there are compelling arguments on both sides. On the positive side, we can see benefits like increased access, improved efficiency, and new opportunities. However, we also need to acknowledge the drawbacks, including potential inequalities, unintended consequences, and challenges to existing systems. I believe the most effective approach involves recognizing that this isn't a binary choice, but rather requires nuanced solutions that can adapt to different contexts.",
            "Well, I'd say this is quite a complex issue. There are several factors to consider. On one hand, there are undeniable advantages - it can make things more accessible, improve quality, and create new possibilities. On the other hand, there are legitimate concerns about negative effects, unequal distribution of benefits, and potential risks. I think the solution lies in finding ways to maximize the positive aspects while addressing the challenges through thoughtful policies and individual responsibility.",
        ]
        
    elif overall <= 7.0:
        templates = [
            "This is a multifaceted issue that requires careful consideration of various factors. On one hand, there are compelling arguments for the benefits it can bring - increased efficiency, enhanced opportunities, and improved quality of life for many. However, we must also acknowledge the potential drawbacks, including unintended consequences, unequal distribution of benefits, and challenges to existing systems. I think the most effective approach involves recognizing that this isn't a binary choice, but rather requires nuanced solutions that can adapt to different contexts. This means considering the perspectives of various stakeholders, understanding long-term implications, and being willing to adjust strategies as we learn more. I believe that thoughtful, evidence-based approaches that prioritize both individual wellbeing and collective good are most likely to succeed.",
            "This represents one of the most pressing and complex challenges of our time, requiring us to navigate multiple competing priorities and perspectives. On one hand, there are undeniable benefits - the potential for increased efficiency, expanded opportunities, and enhanced quality of life. However, we must also grapple with significant concerns, including potential unintended consequences, questions of equity and access, and the ways in which rapid change can disrupt existing social and economic structures. I think the fundamental challenge is recognizing that simplistic solutions are inadequate - we need approaches that can accommodate complexity, adapt to changing circumstances, and balance multiple legitimate interests. This requires not just technical solutions, but also thoughtful consideration of ethical implications, long-term sustainability, and the ways in which different groups will be affected.",
        ]
        
    else:
        templates = [
            "This represents one of the most pressing and complex challenges of our time, requiring us to navigate multiple competing priorities and perspectives. On one hand, there are undeniable benefits - the potential for increased efficiency, expanded opportunities, and enhanced quality of life. However, we must also grapple with significant concerns, including potential unintended consequences, questions of equity and access, and the ways in which rapid change can disrupt existing social and economic structures. I think the fundamental challenge is recognizing that simplistic solutions are inadequate - we need approaches that can accommodate complexity, adapt to changing circumstances, and balance multiple legitimate interests. This requires not just technical solutions, but also thoughtful consideration of ethical implications, long-term sustainability, and the ways in which different groups will be affected. I believe that the most promising path forward involves creating frameworks that can evolve, incorporating diverse perspectives, and maintaining a commitment to both innovation and responsibility.",
        ]
    
    answer = random.choice(templates)
    
    # Добавляем грамматические ошибки в зависимости от GRA
    from improve_generation import add_grammar_errors, add_lexical_limitations
    answer = add_grammar_errors(answer, gra)
    answer = add_lexical_limitations(answer, lr)
    
    return answer, duration

def main():
    print("=" * 70)
    print("TOPIC EXPANSION: Part 3")
    print("=" * 70)
    
    # Загружаем существующие данные
    print("\n📂 Загрузка существующих данных...")
    users, sessions, answers = load_existing_data()
    print(f"   Загружено: {len(users)} пользователей, {len(sessions)} сессий, {len(answers)} ответов")
    
    # Получаем следующие ID
    next_answer_id, next_session_id = get_next_ids(answers)
    print(f"   Следующий answer_id: ans_{next_answer_id:03d}")
    
    # Генерируем новые топики
    topics = generate_modern_part3_topics()
    print(f"\n📝 Подготовлено {len(topics)} новых топиков Part 3")
    
    # Получаем всех пользователей и сессии
    with open('users.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_users = list(reader)
    
    all_user_ids = [u['user_id'] for u in all_users]
    
    with open('sessions.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_sessions = list(reader)
    
    # Генерируем ответы для новых топиков
    # По 2-3 ответа на каждый топик с разными уровнями
    target_count = len(topics) * 2  # 2 ответа на топик
    print(f"\n📝 Генерируем {target_count} новых ответов Part 3...")
    
    new_answers = []
    band_distribution = {
        4.0: 10, 4.5: 8, 5.0: 15, 5.5: 20,
        6.0: 40, 6.5: 25, 7.0: 35, 7.5: 25, 8.0: 12, 8.5: 5
    }
    
    question_idx = 0
    answer_id_counter = next_answer_id
    
    for overall, count in band_distribution.items():
        for _ in range(count):
            if question_idx >= len(topics):
                question_idx = 0
            
            q_id, q_text = topics[question_idx]
            question_idx += 1
            
            # Генерируем субскоры
            fc, lr, gra, pr = generate_realistic_subbands(overall)
            
            # Генерируем ответ
            answer_text, duration = generate_part3_answer_improved(q_text, overall, fc, lr, gra, pr)
            
            # Выбираем пользователя и сессию
            user_id = random.choice(all_user_ids)
            session_id = random.choice([s['session_id'] for s in all_sessions])
            
            # Определяем quality_flag
            from improve_generation import determine_quality_flag
            quality = determine_quality_flag(overall)
            
            # Создаем новый ответ
            new_answer = {
                'answer_id': f'ans_{answer_id_counter:03d}',
                'session_id': session_id,
                'user_id': user_id,
                'part': '3',
                'question_id': q_id,
                'question_text': q_text,
                'answer_text': answer_text,
                'duration_sec': str(duration),
                'target_band_overall': str(overall),
                'target_band_fc': str(fc),
                'target_band_lr': str(lr),
                'target_band_gra': str(gra),
                'target_band_pr': str(pr),
                'transcript_raw': answer_text,
                'source_type': 'synthetic',
                'quality_flag': quality
            }
            
            new_answers.append(new_answer)
            answer_id_counter += 1
    
    # Добавляем новые ответы в answers.csv
    print(f"\n💾 Сохранение {len(new_answers)} новых ответов...")
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
    print(f"   ✅ Добавлено новых топиков: {len(topics)}")
    print(f"   ✅ Добавлено ответов Part 3: {len(new_answers)}")
    
    # Проверка разнообразия субскоров
    varied_3plus = sum(1 for a in new_answers if len(set([
        float(a['target_band_fc']), float(a['target_band_lr']),
        float(a['target_band_gra']), float(a['target_band_pr'])
    ])) >= 3)
    
    print(f"   ✅ Ответов с 3+ уникальными субскорами: {varied_3plus}/{len(new_answers)} ({varied_3plus/len(new_answers)*100:.1f}%)")
    
    print("\n✅ Topic Expansion Part 3 завершен!")

if __name__ == '__main__':
    main()

