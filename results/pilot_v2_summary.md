# E²-Bench Pilot v2 Results — All 3 Levels

## Final Comparison Table

### Level 1: Logical Validation

| Model | Domain | SVA | FPR | FNR | TCA |
|-------|--------|-----|-----|-----|-----|
| gpt-4.1-mini | Code | 30.0% | 100.0% | 0.0% | 30.0% |
| gpt-4.1-mini | Reasoning | 60.0% | 100.0% | 0.0% | 60.0% |
| gpt-4.1-mini | Data Analysis | 20.0% | 100.0% | 0.0% | 20.0% |
| gemini-2.5-flash | Code | 40.0% | 66.7% | 0.0% | 10.0% |
| gemini-2.5-flash | Reasoning | 60.0% | 100.0% | 25.0% | 80.0% |
| gemini-2.5-flash | Data Analysis | 20.0% | 100.0% | 0.0% | 20.0% |

### Level 2: Perceptual Validation

| Model | Recall | Precision | Avg Detection Rate | False Alarms |
|-------|--------|-----------|-------------------|--------------|
| gpt-4.1-mini | 100.0% | 25.9% | 100.0% | 43 |
| gemini-2.5-flash | 100.0% | 35.7% | 100.0% | 27 |

### Level 3: Consistency Validation

| Model | Recall | Precision | Avg Detection Rate | False Alarms |
|-------|--------|-----------|-------------------|--------------|
| gpt-4.1-mini | 82.2% | 97.4% | 80.0% | 1 |
| gemini-2.5-flash | 93.3% | 95.5% | 90.8% | 2 |

## Key Findings

1. **Level 1 (Logical)**: Both models show extreme "Yes Man" bias with FPR 66-100%. They almost never say their own work is wrong.
2. **Level 2 (Perceptual)**: Both models achieve 100% recall on planted UI bugs (from HTML source code alone), but with very low precision (25-36%), generating many false alarms. This suggests they can detect bugs when explicitly asked, but over-report issues.
3. **Level 3 (Consistency)**: Models perform reasonably well (82-93% recall) at finding contradictions, with high precision (95-97%). Gemini slightly outperforms GPT-4.1-mini here.
4. **Cross-level insight**: The validation gap is most severe at Level 1 (logical), moderate at Level 3 (consistency), and inverted at Level 2 (perceptual - high recall but low precision).
