#!/usr/bin/env python3
"""
Скрипт для поиска примеров по профилю субскоров
Помогает проверить "семантическую честность" сложных случаев.
"""

import csv

def load_answers(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def main():
    print("=" * 70)
    print("РУЧНАЯ ПРОВЕРКА ПРОФИЛЕЙ (MINI-V1.1)")
    print("=" * 70)
    
    answers = load_answers('answers_mini_v1.1.csv')
    print(f"📂 Загружено {len(answers)} ответов из mini-v1.1")
    
    # Профили для поиска
    profiles = [
        {
            "name": "Низкий GRA (< 5.0), но высокий LR (> 6.0)",
            "condition": lambda a: float(a['target_band_gra']) < 5.0 and float(a['target_band_lr']) > 6.0
        },
        {
            "name": "Высокий GRA (> 6.0), но низкий FC (< 5.0)",
            "condition": lambda a: float(a['target_band_gra']) > 6.0 and float(a['target_band_fc']) < 5.0
        },
        {
            "name": "Низкий Overall (< 4.5) - проверка на 'garbage'",
            "condition": lambda a: float(a['target_band_overall']) < 4.5
        },
         {
            "name": "Высокий Overall (> 7.5) - проверка на сложность",
            "condition": lambda a: float(a['target_band_overall']) > 7.5
        }
    ]
    
    for profile in profiles:
        print(f"\n🔍 Поиск: {profile['name']}...")
        matches = [a for a in answers if profile['condition'](a)]
        
        if not matches:
            print("   ❌ Нет совпадений")
            continue
            
        # Показываем до 2 примеров
        for i, match in enumerate(matches[:2]):
            print(f"\n   Пример {i+1}:")
            print(f"   Subscores: O={match['target_band_overall']}, FC={match['target_band_fc']}, LR={match['target_band_lr']}, GRA={match['target_band_gra']}, PR={match['target_band_pr']}")
            print(f"   Текст: {match['answer_text']}")
            
            # Быстрый анализ
            text = match['answer_text'].lower()
            if float(match['target_band_gra']) < 5.0:
                 if "he go" in text or "i like book" in text or "i am agree" in text:
                     print("   ✅ Есть маркеры ошибок GRA")
            if float(match['target_band_fc']) < 5.0:
                if "..." in text or "um" in text:
                     print("   ✅ Есть маркеры ошибок FC")
                     
if __name__ == "__main__":
    main()

