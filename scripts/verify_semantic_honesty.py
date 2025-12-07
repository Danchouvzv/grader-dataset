#!/usr/bin/env python3
"""
Скрипт проверки "семантической честности" генерации

Проверяет, соответствуют ли сгенерированные тексты заданным субскорам:
- Низкий GRA -> наличие грамматических ошибок
- Низкий LR -> бедная лексика
- Низкий FC -> проблемы со связностью
"""

from improved_generation_v2 import generate_part1_answer_v2, generate_part2_answer_v2

def check_honesty():
    print("=" * 70)
    print("ПРОВЕРКА СЕМАНТИЧЕСКОЙ ЧЕСТНОСТИ (SEMANTIC HONESTY CHECK)")
    print("=" * 70)
    
    test_cases = [
        {
            "desc": "Низкий GRA (Grammar)",
            "overall": 4.5, "fc": 5.0, "lr": 5.0, "gra": 4.0, "pr": 5.0,
            "question": "Do you like listening to music?",
            "part": 1
        },
        {
            "desc": "Низкий LR (Lexical Resource)",
            "overall": 5.0, "fc": 5.5, "lr": 4.0, "gra": 5.5, "pr": 5.0,
            "question": "Describe a place you visited.",
            "part": 2
        },
        {
            "desc": "Низкий FC (Fluency & Coherence)",
            "overall": 4.5, "fc": 3.5, "lr": 5.0, "gra": 5.0, "pr": 5.0,
            "question": "What kind of weather do you prefer?",
            "part": 1
        },
        {
            "desc": "Высокий уровень (High Level)",
            "overall": 7.5, "fc": 7.5, "lr": 8.0, "gra": 7.5, "pr": 7.5,
            "question": "Describe a book that influenced you.",
            "part": 2
        }
    ]
    
    for case in test_cases:
        print(f"\n🧪 Тест: {case['desc']}")
        print(f"   Subscores: FC={case['fc']}, LR={case['lr']}, GRA={case['gra']}, PR={case['pr']}")
        print(f"   Вопрос: {case['question']}")
        
        if case['part'] == 1:
            answer, _ = generate_part1_answer_v2(
                case['question'], case['overall'], 
                case['fc'], case['lr'], case['gra'], case['pr']
            )
        else:
            answer, _ = generate_part2_answer_v2(
                case['question'], case['overall'], 
                case['fc'], case['lr'], case['gra'], case['pr']
            )
            
        print(f"   Ответ: {answer}")
        
        # Простой анализ
        errors_found = []
        if case['gra'] <= 4.5:
            if "he go" in answer.lower() or "i am agree" in answer.lower() or "i like book" in answer.lower():
                 errors_found.append("Grammar error detected")
        if case['lr'] <= 4.5:
            if answer.lower().count("good") > 1 or answer.lower().count("nice") > 1:
                errors_found.append("Simple vocabulary repetition")
        if case['fc'] <= 4.5:
            if "..." in answer or "um" in answer.lower():
                errors_found.append("Disfluency markers found")
                
        if errors_found:
            print(f"   ✅ Обнаружено: {', '.join(errors_found)}")
        elif case['overall'] >= 7.0:
            if len(answer.split()) > 30:
                print("   ✅ Длинный и сложный ответ (High level)")
        else:
            print("   ⚠️  Явные маркеры не найдены (проверьте глазами)")

if __name__ == "__main__":
    check_honesty()

