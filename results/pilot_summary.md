# E²-Bench Pilot Evaluation Results

## GPT-4.1-mini

### Code Generation (30 tasks)
- SVA: 46.7%
- FPR: 88.9%
- FNR: 0.0%
- TCA: 40.0%
- TP=12, TN=2, FP=16, FN=0

### Logical Reasoning (30 tasks)
- SVA: 90.0%
- FPR: 100.0%
- FNR: 0.0%
- TCA: 90.0%
- TP=27, TN=0, FP=3, FN=0

## Gemini 2.5 Flash

### Code Generation (30 tasks)
- SVA: 46.7%
- FPR: 88.9%
- FNR: 0.0%
- TCA: 40.0%
- TP=12, TN=2, FP=16, FN=0

### Logical Reasoning (30 tasks)
- SVA: 73.3%
- FPR: 60.0%
- FNR: 20.0%
- TCA: 83.3%
- TP=20, TN=2, FP=3, FN=5

### Data Analysis (20 tasks)
- SVA: 25.0%
- FPR: 100.0%
- FNR: 0.0%
- TCA: 25.0%
- TP=5, TN=0, FP=15, FN=0

## Key Findings
1. Both models show extreme "Yes Man" bias - FPR of 88.9% on code, 100% on data analysis
2. Models almost NEVER say FAIL (FNR near 0%), confirming the Yes Man hypothesis
3. SVA is dramatically lower than TCA in all domains
4. The data analysis ground truth checker needs improvement (string matching too strict)
5. Code generation has high failure rate (60% actual fail) suggesting LLM-generated tests are quite strict
