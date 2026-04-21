#!/usr/bin/env python3
"""
E²-Bench Pilot Evaluation v3 — Additional Models
Runs evaluation on gpt-4.1-nano to expand model coverage.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "harness"))
from e2_bench import E2BenchEvaluator

# Additional models to evaluate
MODELS = ["gpt-4.1-nano"]

# Same pilot config as v2
PILOT_CONFIG = {
    # Level 1: Logical
    "code": 10,
    "reasoning": 10,
    "data_analysis": 5,
    # Level 2: Perceptual
    "perceptual": 15,
    # Level 3: Consistency
    "consistency": 10,
}

def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "results", "pilot_v3")
    os.makedirs(output_dir, exist_ok=True)
    
    all_summaries = {}
    
    for model in MODELS:
        print(f"\n{'#'*70}")
        print(f"# MODEL: {model}")
        print(f"{'#'*70}")
        
        evaluator = E2BenchEvaluator(model=model, output_dir=output_dir)
        model_summaries = {}
        
        for domain, num_tasks in PILOT_CONFIG.items():
            print(f"\n--- Running {domain} ({num_tasks} tasks) ---")
            try:
                results = evaluator.run_evaluation(domain, num_tasks)
                metrics = evaluator.compute_metrics(results, domain)
                evaluator.save_results(results, metrics, domain)
                evaluator.print_summary(metrics, domain)
                model_summaries[domain] = metrics
            except Exception as e:
                print(f"ERROR in {domain}: {e}")
                import traceback
                traceback.print_exc()
                model_summaries[domain] = {"error": str(e)}
        
        all_summaries[model] = model_summaries
    
    # Save combined summary
    summary_path = os.path.join(output_dir, "pilot_v3_combined_summary.json")
    with open(summary_path, "w") as f:
        json.dump(all_summaries, f, indent=2)
    print(f"\n\nCombined summary saved to: {summary_path}")
    
    # Print final comparison table
    print(f"\n{'='*80}")
    print("FINAL COMPARISON - ADDITIONAL MODELS")
    print(f"{'='*80}")
    
    for model in MODELS:
        print(f"\n{model}:")
        ms = all_summaries.get(model, {})
        
        # Level 1
        for domain in ["code", "reasoning", "data_analysis"]:
            m = ms.get(domain, {})
            if "error" not in m:
                print(f"  [L1] {domain:15s} SVA={m.get('self_validation_accuracy',0):.1%}  FPR={m.get('false_positive_rate',0):.1%}  TCA={m.get('task_pass_rate',0):.1%}")
        
        # Level 2
        m = ms.get("perceptual", {})
        if "error" not in m:
            print(f"  [L2] {'perceptual':15s} Recall={m.get('overall_recall',0):.1%}  Precision={m.get('overall_precision',0):.1%}  AvgDetRate={m.get('avg_detection_rate',0):.1%}")
        
        # Level 3
        m = ms.get("consistency", {})
        if "error" not in m:
            print(f"  [L3] {'consistency':15s} Recall={m.get('overall_recall',0):.1%}  Precision={m.get('overall_precision',0):.1%}  AvgDetRate={m.get('avg_detection_rate',0):.1%}")

if __name__ == "__main__":
    main()
