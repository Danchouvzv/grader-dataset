# Grader.ai IELTS Speaking Dataset Card (v1.1)

**Date:** 2024
**Version:** v1.1
**Total Size:** 4022 samples
**Language:** English (IELTS simulation)

---

## 1. Dataset Summary

Этот датасет предназначен для обучения и оценки моделей автоматического оценивания IELTS Speaking (Part 1, 2, 3). Он содержит ответы пользователей с целевыми оценками (band scores) по 5 критериям: Overall, Fluency & Coherence (FC), Lexical Resource (LR), Grammatical Range & Accuracy (GRA), Pronunciation (PR).

Датасет является **синтетическим**, с внедрением реалистичных ошибок (error injection) и вариативностью, имитирующей реальных кандидатов разного уровня.

### Composition
- **Part 1 (Interview):** ~1550 samples (Short answers, 10-25 sec)
- **Part 2 (Long Turn):** ~1250 samples (Monologues, 45-70 sec)
- **Part 3 (Discussion):** ~1220 samples (Complex answers, 35-65 sec)

---

## 2. Structure

Датасет состоит из трех связанных таблиц (CSV):

### `users.csv`
Информация о пользователях.
- `user_id`: UUID
- `level_estimate`: Оценка уровня (3.5 - 8.5)
- `registration_date`: Дата регистрации

### `sessions.csv`
Сессии сдачи экзамена.
- `session_id`: ID сессии
- `user_id`: Link to users
- `created_at`: Дата сессии

### `answers.csv` (Main Table)
Отдельные ответы на вопросы.
- `answer_id`: Unique ID
- `part`: 1, 2, or 3
- `question_text`: Текст вопроса
- `answer_text`: Текст ответа (транскрипт)
- `duration_sec`: Длительность аудио (симуляция)
- `target_band_overall`: Итоговая оценка (0.5 step)
- `target_band_fc`, `lr`, `gra`, `pr`: Субскоры
- `source_type`:
    - `synthetic`: Базовая синтетика (v1.0)
    - `synthetic_augmented`: С ASR-шумом
    - `synthetic_v1.1`: Улучшенная генерация с error injection
- `quality_flag`: `ok`, `ok_low`, `garbage`

---

## 3. Version History

### v1.1 (Current)
- **Changes:**
    - Added +1500 samples using improved templates (v2).
    - **Error Injection:** Текст теперь отражает низкие субскоры (GRA < 5 -> grammar errors, FC < 5 -> disfluency).
    - **Semantic Honesty:** Проверено соответствие текста оценкам.
    - **Topic Extraction:** Исправлены баги с артиклями в Part 2.
- **Base:** v1.0 + new generation.

### v1.0 (Baseline)
- Initial release with 2522 samples.
- Basic template generation + ASR noise injection.
- Used for baseline model sanity check.

---

## 4. Methodology

### Generation Pipeline (v1.1)
1.  **Subscore Generation:** Probabilistic model generating varied subscores around `overall` band.
2.  **Text Generation:**
    - **Part 1:** Context-aware templates with discourse markers.
    - **Part 2:** Structured monologues (Intro -> Background -> Main Body -> Reflection).
    - **Part 3:** Complex argumentative structures.
3.  **Error Injection (Tier 2):**
    - **GRA:** Injection of tense errors, article omission, wrong word order based on GRA score.
    - **LR:** Vocabulary simplification and repetition for low LR.
    - **FC:** Insertion of fillers ("um", "uh"), self-corrections, and breaks for low FC.
    - **PR:** Modeled via ASR artifacts.

### Validation
- **Baseline Model (RF + TF-IDF):** MAE ~0.29 on Overall Band. High correlation (0.91).
- **Manual Review:** Semantic honesty verified for edge cases (e.g., Low GRA/High LR).

---

## 5. Usage & Limitations

### Intended Use
- Pre-training of IELTS grading models.
- Testing multi-task learning architectures (predicting subscores).
- Analysis of feature importance for different bands.

### Limitations
- **Synthetic Nature:** Data is generated, not recorded from real humans. May lack nuances of spontaneous speech.
- **No Audio:** Only text transcripts and duration features.
- **Bias:** Templates might introduce specific patterns that the model could overfit to.
- **High-Band Scarcity:** Fewer samples for bands 8.0-9.0 compared to 5.0-6.5.

---

**Maintainer:** Grader.ai Team

