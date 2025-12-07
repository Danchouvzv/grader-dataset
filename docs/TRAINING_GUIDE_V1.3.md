# Training Guide for v1.3

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
