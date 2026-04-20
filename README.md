# E²-Bench: Eval of Eval for Measuring Self-Validation Reliability in LLM Agents

## Overview

E²-Bench is a novel benchmark that systematically measures the **self-validation reliability** of LLM agents. While existing benchmarks evaluate whether an agent can solve a task (Task Completion Accuracy), E²-Bench evaluates whether the agent can **accurately judge its own work** (Self-Validation Accuracy).

The key insight is that when an LLM agent says "I have verified this is correct," that verification itself may be unreliable. We call this the **"Yes Man" bias** — the tendency of LLMs to approve their own outputs even when they contain errors.

## Repository Structure

```
e2_bench/
├── README.md                          # This file
├── eval_set/                          # The benchmark dataset (500 tasks)
│   ├── code_generation/
│   │   └── tasks.json                 # 200 code generation tasks
│   ├── data_analysis/
│   │   └── tasks.json                 # 150 data analysis tasks
│   └── logical_reasoning/
│       └── tasks.json                 # 150 logical reasoning tasks
├── harness/
│   └── e2_bench.py                    # Core evaluation framework
├── scripts/
│   ├── generate_code_tasks.py         # Code task generator
│   ├── generate_data_analysis_tasks.py # Data analysis task generator
│   ├── generate_reasoning_tasks.py    # Reasoning task generator
│   ├── run_pilot.py                   # Pilot evaluation runner
│   └── analyze_results.py            # Results analysis & figure generation
├── results/                           # Pilot evaluation results
│   ├── *_metrics.json                 # Per-model per-domain metrics
│   ├── *_results.json                 # Detailed per-task results
│   └── pilot_summary.md              # Summary of pilot findings
└── paper/
    ├── main.tex                       # LaTeX paper source
    ├── main.pdf                       # Compiled paper (8 pages)
    └── figures/                       # Generated figures
        ├── fig1_sva_vs_tca.png
        ├── fig2_fpr_heatmap.png
        ├── fig3_confusion_matrices.png
        ├── fig4_validation_gap.png
        └── fig5_outcome_distribution.png
```

## Key Metrics

E²-Bench introduces four key metrics for measuring self-validation reliability:

| Metric | Definition | What It Measures |
|--------|-----------|-----------------|
| **SVA** (Self-Validation Accuracy) | Accuracy of the agent's self-assessment | Overall reliability of self-validation |
| **FPR** (False Positive Rate) | Rate of approving incorrect outputs | "Yes Man" bias severity |
| **FNR** (False Negative Rate) | Rate of rejecting correct outputs | "Over-thinker" bias severity |
| **TCA** (Task Completion Accuracy) | Rate of actually correct solutions | Baseline task performance |

## Pilot Results (GPT-4.1-mini, Gemini 2.5 Flash)

| Model | Domain | SVA | FPR | FNR | TCA |
|-------|--------|-----|-----|-----|-----|
| GPT-4.1-mini | Code Generation | 46.7% | **88.9%** | 0.0% | 40.0% |
| GPT-4.1-mini | Logical Reasoning | 90.0% | **100.0%** | 0.0% | 90.0% |
| Gemini 2.5 Flash | Code Generation | 46.7% | **88.9%** | 0.0% | 40.0% |
| Gemini 2.5 Flash | Logical Reasoning | 73.3% | **60.0%** | 20.0% | 83.3% |
| Gemini 2.5 Flash | Data Analysis | 25.0% | **100.0%** | 0.0% | 25.0% |

**Key Finding**: Both models exhibit extreme "Yes Man" bias with FPR of 60-100%, meaning they almost always approve their own outputs regardless of correctness.

## Quick Start

### Running an Evaluation

```python
from harness.e2_bench import E2BenchEvaluator

evaluator = E2BenchEvaluator(model="gpt-4.1-mini", output_dir="./results")

# Run code generation evaluation (30 task sample)
results = evaluator.run_evaluation("code", num_tasks=30)
metrics = evaluator.compute_metrics(results)
evaluator.save_results(results, metrics, "code")

print(f"SVA: {metrics['self_validation_accuracy']:.1%}")
print(f"FPR: {metrics['false_positive_rate']:.1%}")
```

### Generating Figures

```bash
python scripts/analyze_results.py
```

## Two-Stage Forced Verification Protocol

E²-Bench uses a novel evaluation protocol that decouples generation from verification:

1. **Stage 1 (Generation)**: The agent generates a solution to the task.
2. **Stage 2 (Forced Verification)**: The agent is explicitly asked to verify its own solution and output a binary verdict (`VERIFIED_PASS` or `VERIFIED_FAIL`).
3. **Ground Truth Check**: The solution is independently verified against hidden test suites / pre-computed answers.

The agent's verdict is then compared to ground truth to classify the outcome as TP, TN, FP, or FN.

## Requirements

- Python 3.11+
- `openai` package (for API access)
- Environment variable: `OPENAI_API_KEY`

## Citation

```bibtex
@article{e2bench2026,
  title={E$^2$-Bench: Eval of Eval for Measuring Self-Validation Reliability in LLM Agents},
  author={Anonymous},
  journal={arXiv preprint},
  year={2026}
}
```

## License

MIT License
