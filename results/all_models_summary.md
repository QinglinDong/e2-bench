# E²-Bench: All Models Results Summary

## 3 Models Evaluated: GPT-4.1-mini, Gemini 2.5 Flash, GPT-4.1-nano

### Level 1: Logical Validation

| Model | Domain | SVA | FPR | FNR | TCA |
|-------|--------|-----|-----|-----|-----|
| GPT-4.1-mini | Code | 30.0% | 100.0% | 0.0% | 30.0% |
| GPT-4.1-mini | Reasoning | 60.0% | 100.0% | 0.0% | 60.0% |
| GPT-4.1-mini | Data Analysis | 20.0% | 100.0% | 0.0% | 20.0% |
| Gemini 2.5 Flash | Code | 40.0% | 66.7% | 0.0% | 10.0% |
| Gemini 2.5 Flash | Reasoning | 60.0% | 100.0% | 25.0% | 80.0% |
| Gemini 2.5 Flash | Data Analysis | 20.0% | 100.0% | 0.0% | 20.0% |
| GPT-4.1-nano | Code | 30.0% | 100.0% | 0.0% | 30.0% |
| GPT-4.1-nano | Reasoning | 60.0% | 80.0% | 0.0% | 50.0% |
| GPT-4.1-nano | Data Analysis | 20.0% | 100.0% | 0.0% | 20.0% |

### Level 2: Perceptual Validation

| Model | Recall | Precision | F1 | False Alarms |
|-------|--------|-----------|-----|-------------|
| GPT-4.1-mini | 100.0% | 25.9% | 41.1% | 43 |
| Gemini 2.5 Flash | 100.0% | 35.7% | 52.6% | 27 |
| GPT-4.1-nano | 100.0% | 26.8% | 42.3% | 41 |

### Level 3: Consistency Validation

| Model | Recall | Precision | Avg Detection Rate |
|-------|--------|-----------|-------------------|
| GPT-4.1-mini | 82.2% | 78.7% | 73.0% |
| Gemini 2.5 Flash | 93.3% | 72.4% | 85.0% |
| GPT-4.1-nano | 62.2% | 82.3% | 60.2% |

## Key Findings

1. **Yes Man Bias is universal**: FPR ranges from 66.7% to 100% across all models at Level 1
2. **Perceptual over-reporting**: All models achieve 100% recall but catastrophic precision (26-36%), meaning they report 2-4x more bugs than actually exist
3. **Consistency scales with model size**: Gemini 2.5 Flash > GPT-4.1-mini > GPT-4.1-nano on recall
4. **No model is reliable**: Even the best model (Gemini) has 67% FPR on code validation
