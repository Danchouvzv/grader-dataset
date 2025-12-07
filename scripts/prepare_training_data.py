#!/usr/bin/env python3
"""
Подготовка данных для обучения модели
- Загружает train/val/test
- Добавляет метаданные для multi-task обучения
- Создает конфиг для обучения
"""

import csv
import json
from collections import defaultdict

def analyze_split(split_file: str, split_name: str):
    """Анализирует split и возвращает статистику"""
    with open(split_file, 'r', encoding='utf-8') as f:
        answers = list(csv.DictReader(f))
    
    stats = {
        'total': len(answers),
        'by_part': defaultdict(int),
        'by_band_group': defaultdict(int),
        'by_quality': defaultdict(int),
        'by_source': defaultdict(int),
        'weighted_count': 0,
        'inconsistent_count': 0,
    }
    
    for answer in answers:
        part = answer.get('part', '')
        stats['by_part'][part] += 1
        
        try:
            overall = float(answer.get('target_band_overall', 0))
            if overall <= 5.5:
                band_group = 'low'
            elif overall <= 6.5:
                band_group = 'mid'
            else:
                band_group = 'high'
            stats['by_band_group'][band_group] += 1
        except:
            pass
        
        quality = answer.get('quality_flag', 'ok')
        stats['by_quality'][quality] += 1
        
        source = answer.get('source_type', 'unknown')
        stats['by_source'][source] += 1
        
        weight = float(answer.get('sample_weight', 1.0))
        if weight < 1.0:
            stats['weighted_count'] += 1
        
        if answer.get('is_inconsistent', 'false') == 'true':
            stats['inconsistent_count'] += 1
    
    return stats

def main():
    print("=" * 70)
    print("ПОДГОТОВКА ДАННЫХ ДЛЯ ОБУЧЕНИЯ")
    print("=" * 70)
    
    splits = {
        'train': 'dataset_versions/v1.3/train.csv',
        'val': 'dataset_versions/v1.3/val.csv',
        'test': 'dataset_versions/v1.3/test.csv'
    }
    
    all_stats = {}
    
    for split_name, split_file in splits.items():
        print(f"\n📊 Анализ {split_name.upper()}:")
        stats = analyze_split(split_file, split_name)
        all_stats[split_name] = stats
        
        print(f"   Всего: {stats['total']} ответов")
        print(f"   По частям:")
        for part in sorted(stats['by_part'].keys()):
            count = stats['by_part'][part]
            print(f"      Part {part}: {count} ({count/stats['total']*100:.1f}%)")
        
        print(f"   По бэндам:")
        for band in ['low', 'mid', 'high']:
            count = stats['by_band_group'].get(band, 0)
            if count > 0:
                print(f"      {band}: {count} ({count/stats['total']*100:.1f}%)")
        
        print(f"   Weighted: {stats['weighted_count']} ({stats['weighted_count']/stats['total']*100:.1f}%)")
        print(f"   Inconsistent: {stats['inconsistent_count']} ({stats['inconsistent_count']/stats['total']*100:.1f}%)")
    
    # Создаем конфиг для обучения
    config = {
        'dataset_version': 'v1.3',
        'splits': {
            'train': {
                'file': 'dataset_versions/v1.3/train.csv',
                'count': all_stats['train']['total'],
                'weighted_count': all_stats['train']['weighted_count'],
                'inconsistent_count': all_stats['train']['inconsistent_count']
            },
            'val': {
                'file': 'dataset_versions/v1.3/val.csv',
                'count': all_stats['val']['total']
            },
            'test': {
                'file': 'dataset_versions/v1.3/test.csv',
                'count': all_stats['test']['total']
            }
        },
        'targets': {
            'main': 'target_band_overall',
            'subscores': ['target_band_fc', 'target_band_lr', 'target_band_gra', 'target_band_pr']
        },
        'features': {
            'text': 'answer_text',
            'metadata': ['part', 'duration_sec', 'quality_flag', 'source_type']
        },
        'training': {
            'use_sample_weights': True,
            'weight_column': 'sample_weight',
            'multi_task': True,
            'calibration': {
                'round_to_half_band': True,
                'threshold': 0.5
            }
        },
        'metrics': {
            'regression': ['mae', 'mse', 'rmse'],
            'classification': ['accuracy_within_0.5', 'accuracy_within_1.0'],
            'per_part': True,
            'per_band_group': True
        }
    }
    
    config_file = 'configs/training_config_v1.3.json'
    import os
    os.makedirs('configs', exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n💾 Конфиг сохранен в {config_file}")
    
    # Создаем README для обучения
    readme = """# Training Guide for v1.3

## Dataset Overview

- **Version:** v1.3 (Clean & Validated)
- **Total answers:** 4264
- **Train/Val/Test:** 79.2% / 9.3% / 11.5%

## Training Configuration

### Main Task
- **Target:** `target_band_overall` (regression)
- **Loss:** MSE / MAE
- **Calibration:** Round to 0.5-band scale

### Multi-task
- **Subscores:** FC, LR, GRA, PR (separate heads)
- **Weight:** Can be weighted by importance

### Sample Weights
- **Normal answers:** weight = 1.0
- **Inconsistent (weighted):** weight = 0.4-0.6
- **Use in training:** Set `use_sample_weights=True`

## Metrics

### Regression
- MAE (Mean Absolute Error)
- MSE (Mean Squared Error)
- RMSE (Root Mean Squared Error)

### Classification (after calibration)
- Accuracy within ±0.5 band
- Accuracy within ±1.0 band

### Per-segment
- By Part (1, 2, 3)
- By Band group (low, mid, high)

## Training Steps

1. **Load data:**
   ```python
   train = pd.read_csv('dataset_versions/v1.3/train.csv')
   val = pd.read_csv('dataset_versions/v1.3/val.csv')
   test = pd.read_csv('dataset_versions/v1.3/test.csv')
   ```

2. **Prepare features:**
   - Text: `answer_text`
   - Metadata: `part`, `duration_sec`, `quality_flag`

3. **Prepare targets:**
   - Main: `target_band_overall`
   - Subscores: `target_band_fc`, `target_band_lr`, `target_band_gra`, `target_band_pr`

4. **Sample weights:**
   ```python
   train_weights = train['sample_weight'].astype(float)
   ```

5. **Train model:**
   - Use encoder (BERT/DistilBERT) for text
   - Multi-task heads for subscores
   - Apply sample weights in loss

6. **Evaluate:**
   - Raw predictions (MAE)
   - Calibrated predictions (accuracy within ±0.5)

## Next Steps

1. Collect real-world eval set (50-100 answers)
2. Compare model performance on synthetic vs real
3. Fine-tune based on real data feedback
"""
    
    readme_file = 'docs/TRAINING_GUIDE_V1.3.md'
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print(f"💾 Training guide сохранен в {readme_file}")
    print(f"\n✅ Подготовка данных завершена")

if __name__ == '__main__':
    main()

