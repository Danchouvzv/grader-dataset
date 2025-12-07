# IELTS Speaking Dataset

Структурированный датасет для обучения моделей оценки IELTS Speaking.

## Структура датасета

### Таблицы

1. **users.csv** - Пользователи
   - `user_id` (UUID)
   - `level_estimate` (float, опционально)
   - `registration_date` (datetime)

2. **sessions.csv** - Сессии тренировок
   - `session_id`
   - `user_id` (FK)
   - `created_at` (datetime)
   - `target_exam_date` (datetime, опционально)

3. **answers.csv** - Ответы пользователей
   - `answer_id`
   - `session_id` (FK)
   - `user_id` (FK)
   - `part` (1/2/3)
   - `question_id`
   - `question_text`
   - `answer_text`
   - `duration_sec`
   - `target_band_overall`
   - `target_band_fc` (Fluency & Coherence)
   - `target_band_lr` (Lexical Resource)
   - `target_band_gra` (Grammatical Range & Accuracy)
   - `target_band_pr` (Pronunciation)
   - `transcript_raw`
   - `source_type`
   - `quality_flag` (ok/garbage)

## Порядок запуска скриптов

⚠️ **ВАЖНО**: Скрипты нужно запускать в строгом порядке!

### 1. Базовый датасет

Сначала создайте базовый датасет с ответами (вручную или другим скриптом).

### 2. Улучшение датасета

```bash
python3 enhance_dataset.py
```

**Что делает:**
- Добавляет реалистичный разброс субскоров вокруг overall
- Добавляет поля: `transcript_raw`, `source_type`, `quality_flag`
- Добавляет вариацию ±0.5 band относительно уровня пользователя
- **Идемпотентен**: не трогает ответы с `quality_flag='garbage'`

### 3. Добавление "убитых" ответов

```bash
python3 add_trash_answers.py
```

**Что делает:**
- Добавляет 30 ответов уровня 3.5-4.5 с максимально корявыми текстами
- Создает новых слабых пользователей если нужно
- **ВАЖНО**: Запускать ПОСЛЕ `enhance_dataset.py`

### 4. EDA анализ

```bash
python3 eda.py
```

**Что делает:**
- Анализирует распределения по уровням, длительности, субскорам
- Разделяет анализ по частям (Part 1/2/3)
- Создает гистограммы:
  - `eda_overall_duration.png`
  - `eda_subbands.png`
  - `eda_users.png`
  - `eda_quality_flag.png`

## Требования

```bash
pip install matplotlib numpy
```

## Статистика датасета

После обработки датасет содержит:
- ~100 ответов
- ~40 пользователей
- ~45 сессий
- Распределение по уровням: 3.0-8.5 (среднее ~5.4)
- Разброс субскоров: std ≈ 1.4-1.6

## Особенности

### Реалистичный разброс субскоров

- У слабых уровней (4.0-5.5) чаще проседают GRA/PR
- У сильных (7.0+) выше LR/FC
- У русскоязычных часто LR > GRA

### ASR-артефакты

Ответы содержат:
- Filler-слова: "um", "uh", "like", "you know"
- Паузы: "..."
- Самокоррекцию
- Отсутствие капитализации
- Повторы

### Quality Flags

- `ok` - нормальные ответы для обучения
- `garbage` - очень корявые ответы (можно фильтровать при обучении)

## Использование для ML

Датасет готов для:
- TF-IDF + линейные модели
- CatBoost / XGBoost
- Multi-task обучение (5 целевых переменных)
- Ordinal regression

## Примечания

- Все скрипты используют `random.seed(42)` для воспроизводимости
- Скрипты идемпотентны (можно запускать несколько раз безопасно)
- `enhance_dataset.py` не трогает garbage-ответы после первого запуска

