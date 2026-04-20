"""
E²-Bench Pilot Evaluation
Run a sample of tasks from each domain to get initial results.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'harness'))

from e2_bench import E2BenchEvaluator

def main():
    output_dir = "/home/ubuntu/e2_bench/results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Evaluate with gpt-4.1-mini
    models = ["gpt-4.1-mini", "gemini-2.5-flash"]
    
    for model_name in models:
        print(f"\n{'#'*70}")
        print(f"# Evaluating model: {model_name}")
        print(f"{'#'*70}")
        
        evaluator = E2BenchEvaluator(model=model_name, output_dir=output_dir)
        
        # Code generation: 30 task sample
        print("\n>>> Code Generation (30 tasks sample)")
        try:
            code_results = evaluator.run_evaluation("code", num_tasks=30)
            code_metrics = evaluator.compute_metrics(code_results)
            evaluator.save_results(code_results, code_metrics, "code")
            print_metrics(code_metrics)
        except Exception as e:
            print(f"Error in code evaluation: {e}")
            code_metrics = {}
        
        # Reasoning: 30 task sample
        print("\n>>> Logical Reasoning (30 tasks sample)")
        try:
            reason_results = evaluator.run_evaluation("reasoning", num_tasks=30)
            reason_metrics = evaluator.compute_metrics(reason_results)
            evaluator.save_results(reason_results, reason_metrics, "reasoning")
            print_metrics(reason_metrics)
        except Exception as e:
            print(f"Error in reasoning evaluation: {e}")
            reason_metrics = {}
        
        # Data analysis: try if available
        data_tasks_path = "/home/ubuntu/e2_bench/eval_set/data_analysis/tasks.json"
        if os.path.exists(data_tasks_path):
            print("\n>>> Data Analysis (20 tasks sample)")
            try:
                data_results = evaluator.run_evaluation("data_analysis", num_tasks=20)
                data_metrics = evaluator.compute_metrics(data_results)
                evaluator.save_results(data_results, data_metrics, "data_analysis")
                print_metrics(data_metrics)
            except Exception as e:
                print(f"Error in data analysis evaluation: {e}")
        else:
            print("\n>>> Data Analysis: tasks not yet generated, skipping")

def print_metrics(metrics):
    print(f"\n  --- Metrics Summary ---")
    print(f"  SVA:  {metrics.get('self_validation_accuracy', 0):.1%}")
    print(f"  FPR:  {metrics.get('false_positive_rate', 0):.1%}")
    print(f"  FNR:  {metrics.get('false_negative_rate', 0):.1%}")
    print(f"  TCA:  {metrics.get('task_pass_rate', 0):.1%}")
    print(f"  TP={metrics.get('true_positives',0)} TN={metrics.get('true_negatives',0)} FP={metrics.get('false_positives',0)} FN={metrics.get('false_negatives',0)}")

if __name__ == "__main__":
    main()
