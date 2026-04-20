"""
E²-Bench: Eval of Eval — Evaluation Harness
=============================================
A benchmark for measuring self-validation reliability in LLM agents.

Three levels of validation:
  Level 1 - Logical:     Code, Data Analysis, Reasoning (objective ground truth)
  Level 2 - Perceptual:  UI/UX bug detection in HTML artifacts (planted bugs)
  Level 3 - Consistency: Cross-context contradiction detection (planted contradictions)

Usage:
    python e2_bench.py --model gpt-4.1-mini --domain code --num_tasks 10
    python e2_bench.py --model gpt-4.1-mini --domain perceptual --num_tasks 10
    python e2_bench.py --model gpt-4.1-mini --domain consistency --num_tasks 10
    python e2_bench.py --model gpt-4.1-mini --domain all --output results/
"""

import json
import os
import re
import sys
import argparse
import subprocess
import tempfile
import time
from datetime import datetime
from typing import Optional
from openai import OpenAI

# ============================================================
# Configuration
# ============================================================
LEVEL1_DOMAINS = ["code", "data_analysis", "reasoning"]
LEVEL2_DOMAINS = ["perceptual"]
LEVEL3_DOMAINS = ["consistency"]
ALL_DOMAINS = LEVEL1_DOMAINS + LEVEL2_DOMAINS + LEVEL3_DOMAINS

EVAL_SET_DIR = os.path.join(os.path.dirname(__file__), "..", "eval_set")

# ============================================================
# Level 1: Logical Validation Prompts
# ============================================================

CODE_GEN_PROMPT = """You are an expert Python developer. Please solve the following programming task.
Return ONLY the Python code containing the function implementation. Do not include test code, explanations, or markdown formatting.

Task:
{description}

Function signature: {function_signature}
"""

CODE_VERIFY_PROMPT = """You are an expert code reviewer and QA engineer. Your task is to rigorously verify the correctness of a provided Python solution.

Task Description:
{description}

Function Signature: {function_signature}

Provided Solution:
```python
{solution}
```

Instructions:
1. Carefully analyze the solution against ALL task requirements.
2. Consider edge cases: empty inputs, single elements, large values, negative numbers, etc.
3. Write a comprehensive set of unit tests (using assert statements) to verify correctness.
4. Execute the tests mentally and determine if the solution passes all of them.
5. Make a final binary decision: is this solution COMPLETELY correct?

You MUST respond with a JSON object in exactly this format (no markdown, no extra text):
{{"critique": "Your detailed analysis...", "generated_tests": "assert func(...) == ...\\nassert func(...) == ...", "final_decision": "VERIFIED_PASS"}}

The final_decision MUST be exactly "VERIFIED_PASS" or "VERIFIED_FAIL"."""

DATA_GEN_PROMPT = """You are an expert data analyst. You are given a dataset with the following schema:
{dataset_schema}

Sample data:
{dataset_csv_snippet}

Task:
{description}

Please provide your analysis and the final answer. Show your reasoning or the Python/pandas code you would use.
"""

DATA_VERIFY_PROMPT = """You are a senior data scientist reviewing an analyst's work.

Dataset Schema:
{dataset_schema}

Task Description:
{description}

Provided Solution & Answer:
{solution}

Instructions:
1. Review the methodology step by step.
2. Check for common pitfalls: off-by-one errors, incorrect filtering, wrong aggregation, missing null handling.
3. Verify the final answer is reasonable and correctly computed.
4. Make a final binary decision on correctness.

You MUST respond with a JSON object in exactly this format (no markdown, no extra text):
{{"critique": "Your detailed review...", "final_decision": "VERIFIED_PASS"}}

The final_decision MUST be exactly "VERIFIED_PASS" or "VERIFIED_FAIL"."""

REASONING_GEN_PROMPT = """You are an expert logician and mathematician. Please solve the following puzzle/problem.
Show your complete step-by-step reasoning, then state your final answer clearly.

Problem:
{description}
"""

REASONING_VERIFY_PROMPT = """You are a strict logic verifier. Your job is to check a proposed solution to a reasoning problem.

Problem:
{description}

Proposed Solution:
{solution}

Instructions:
1. Go through the proposed solution step by step.
2. Check each logical step for validity.
3. Verify that all constraints/conditions of the problem are satisfied.
4. Verify the final answer is correct.
5. Make a final binary decision.

You MUST respond with a JSON object in exactly this format (no markdown, no extra text):
{{"critique": "Your step-by-step verification...", "final_decision": "VERIFIED_PASS"}}

The final_decision MUST be exactly "VERIFIED_PASS" or "VERIFIED_FAIL"."""

# ============================================================
# Level 2: Perceptual Validation Prompts
# ============================================================

PERCEPTUAL_DETECT_PROMPT = """You are an expert UI/UX quality assurance engineer. You are given the HTML source code of a web page that was generated by an AI assistant.

Your task is to carefully review the HTML and CSS to identify any visual bugs, UI issues, or quality problems that a human user would immediately notice.

HTML Source Code:
```html
{html_code}
```

Page Description: {page_description}

Instructions:
1. Analyze the HTML and CSS carefully.
2. Look for common UI bugs: image sizing/aspect ratio issues, text contrast problems, broken layouts, missing elements, misalignment, z-index issues, overflow problems, unclickable buttons, etc.
3. Think about what a human user would see when this page is rendered in a browser.
4. List ALL bugs you find, no matter how small.

You MUST respond with a JSON object in exactly this format (no markdown, no extra text):
{{"bugs_found": ["description of bug 1", "description of bug 2", ...], "num_bugs_found": 2, "confidence": "high"}}

If you find NO bugs, respond with:
{{"bugs_found": [], "num_bugs_found": 0, "confidence": "high"}}"""

# ============================================================
# Level 3: Consistency Validation Prompts
# ============================================================

CONSISTENCY_DETECT_PROMPT = """You are an expert document reviewer and quality assurance specialist. You are given a multi-part artifact (such as a report, codebase, or documentation set) that was generated by an AI assistant.

Your task is to carefully check for INTERNAL CONTRADICTIONS between different parts of the artifact. A contradiction is when two parts of the same artifact state conflicting information.

Artifact Description: {description}

{artifact_parts_formatted}

Instructions:
1. Read each part carefully and extract key claims, numbers, names, and specifications.
2. Cross-reference information between ALL parts.
3. Identify any contradictions where one part says X but another part says Y.
4. Be specific: quote the exact conflicting statements from each part.
5. List ALL contradictions you find.

You MUST respond with a JSON object in exactly this format (no markdown, no extra text):
{{"contradictions_found": ["description of contradiction 1", "description of contradiction 2", ...], "num_contradictions_found": 2, "confidence": "high"}}

If you find NO contradictions, respond with:
{{"contradictions_found": [], "num_contradictions_found": 0, "confidence": "high"}}"""


# ============================================================
# Core Evaluation Engine
# ============================================================

class E2BenchEvaluator:
    def __init__(self, model: str, output_dir: str = "results"):
        self.client = OpenAI()
        self.model = model
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def call_llm(self, prompt: str, system: str = "You are a helpful assistant.") -> str:
        """Call the LLM and return the response text."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=4096
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def parse_json_response(self, response: str) -> dict:
        """Parse a JSON response from the LLM."""
        # Try direct JSON parse
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON in markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find any JSON object in the response
        # Use a more permissive pattern that handles nested arrays
        brace_start = response.find('{')
        if brace_start != -1:
            depth = 0
            for i in range(brace_start, len(response)):
                if response[i] == '{':
                    depth += 1
                elif response[i] == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(response[brace_start:i+1])
                        except json.JSONDecodeError:
                            break
        
        # Fallback for verification responses
        if "VERIFIED_PASS" in response:
            return {"critique": response, "final_decision": "VERIFIED_PASS"}
        elif "VERIFIED_FAIL" in response:
            return {"critique": response, "final_decision": "VERIFIED_FAIL"}
        
        return {"raw": response, "parse_error": True}
    
    # ============================================================
    # Level 1: Logical Validation
    # ============================================================
    
    def evaluate_code_task(self, task: dict) -> dict:
        """Run the two-stage protocol for a code generation task."""
        gen_prompt = CODE_GEN_PROMPT.format(
            description=task["description"],
            function_signature=task["function_signature"]
        )
        solution = self.call_llm(gen_prompt)
        
        verify_prompt = CODE_VERIFY_PROMPT.format(
            description=task["description"],
            function_signature=task["function_signature"],
            solution=solution
        )
        verify_response = self.call_llm(verify_prompt)
        verification = self.parse_json_response(verify_response)
        
        actual_pass = self._run_code_tests(solution, task)
        model_says_pass = verification.get("final_decision") == "VERIFIED_PASS"
        
        return {
            "task_id": task.get("task_id", "unknown"),
            "level": "L1_logical",
            "domain": "code",
            "category": task.get("category", "unknown"),
            "difficulty": task.get("difficulty", "unknown"),
            "model": self.model,
            "stage1_solution": solution,
            "stage2_verification": verification,
            "model_decision": "PASS" if model_says_pass else "FAIL",
            "actual_result": "PASS" if actual_pass else "FAIL",
            "outcome": self._classify_outcome(model_says_pass, actual_pass),
            "timestamp": datetime.now().isoformat()
        }
    
    def _run_code_tests(self, solution: str, task: dict) -> bool:
        """Execute the solution against hidden tests in a sandbox."""
        solution_clean = solution.strip()
        if solution_clean.startswith("```"):
            lines = solution_clean.split("\n")
            solution_clean = "\n".join(lines[1:])
            if solution_clean.endswith("```"):
                solution_clean = solution_clean[:-3]
        
        test_code = f"""{solution_clean}

# Hidden tests
{task.get('hidden_tests', '')}
print("ALL_TESTS_PASSED")
"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_code)
                f.flush()
                result = subprocess.run(
                    ['python3', f.name],
                    capture_output=True, text=True, timeout=10
                )
                os.unlink(f.name)
                return "ALL_TESTS_PASSED" in result.stdout
        except Exception:
            return False
    
    def evaluate_data_task(self, task: dict) -> dict:
        """Run the two-stage protocol for a data analysis task."""
        gen_prompt = DATA_GEN_PROMPT.format(
            dataset_schema=task.get("dataset_schema", ""),
            dataset_csv_snippet=task.get("dataset_csv_snippet", ""),
            description=task["description"]
        )
        solution = self.call_llm(gen_prompt)
        
        verify_prompt = DATA_VERIFY_PROMPT.format(
            dataset_schema=task.get("dataset_schema", ""),
            description=task["description"],
            solution=solution
        )
        verify_response = self.call_llm(verify_prompt)
        verification = self.parse_json_response(verify_response)
        
        actual_pass = self._check_data_answer(solution, task)
        model_says_pass = verification.get("final_decision") == "VERIFIED_PASS"
        
        return {
            "task_id": task.get("task_id", "unknown"),
            "level": "L1_logical",
            "domain": "data_analysis",
            "category": task.get("category", "unknown"),
            "difficulty": task.get("difficulty", "unknown"),
            "model": self.model,
            "stage1_solution": solution,
            "stage2_verification": verification,
            "model_decision": "PASS" if model_says_pass else "FAIL",
            "actual_result": "PASS" if actual_pass else "FAIL",
            "outcome": self._classify_outcome(model_says_pass, actual_pass),
            "ground_truth_answer": task.get("ground_truth_answer", ""),
            "timestamp": datetime.now().isoformat()
        }
    
    def _check_data_answer(self, solution: str, task: dict) -> bool:
        gt = str(task.get("ground_truth_answer", "")).strip().lower()
        return gt in solution.lower()
    
    def evaluate_reasoning_task(self, task: dict) -> dict:
        """Run the two-stage protocol for a reasoning task."""
        gen_prompt = REASONING_GEN_PROMPT.format(description=task["description"])
        solution = self.call_llm(gen_prompt)
        
        verify_prompt = REASONING_VERIFY_PROMPT.format(
            description=task["description"],
            solution=solution
        )
        verify_response = self.call_llm(verify_prompt)
        verification = self.parse_json_response(verify_response)
        
        actual_pass = self._check_reasoning_answer(solution, task)
        model_says_pass = verification.get("final_decision") == "VERIFIED_PASS"
        
        return {
            "task_id": task.get("task_id", "unknown"),
            "level": "L1_logical",
            "domain": "reasoning",
            "category": task.get("category", "unknown"),
            "difficulty": task.get("difficulty", "unknown"),
            "model": self.model,
            "stage1_solution": solution,
            "stage2_verification": verification,
            "model_decision": "PASS" if model_says_pass else "FAIL",
            "actual_result": "PASS" if actual_pass else "FAIL",
            "outcome": self._classify_outcome(model_says_pass, actual_pass),
            "ground_truth_answer": task.get("ground_truth_answer", ""),
            "timestamp": datetime.now().isoformat()
        }
    
    def _check_reasoning_answer(self, solution: str, task: dict) -> bool:
        gt = str(task.get("ground_truth_answer", "")).strip().lower()
        solution_lower = solution.lower()
        if task.get("type") == "game_of_24":
            is_solvable = task.get("ground_truth_solvable", True)
            if is_solvable:
                return "yes" in solution_lower and "not possible" not in solution_lower
            else:
                return "no" in solution_lower or "not possible" in solution_lower or "impossible" in solution_lower
        return gt in solution_lower
    
    # ============================================================
    # Level 2: Perceptual Validation
    # ============================================================
    
    def evaluate_perceptual_task(self, task: dict) -> dict:
        """Evaluate if the model can detect planted UI bugs in HTML."""
        bugged_html = task.get("bugged_html", "")
        page_desc = task.get("page_description", "")
        
        detect_prompt = PERCEPTUAL_DETECT_PROMPT.format(
            html_code=bugged_html,
            page_description=page_desc
        )
        
        response = self.call_llm(detect_prompt, system="You are an expert UI/UX quality assurance engineer.")
        parsed = self.parse_json_response(response)
        
        # Ground truth
        gt_bugs = task.get("ground_truth", [])
        found_bugs = parsed.get("bugs_found", [])
        
        # Compute detection metrics
        detection_result = self._score_perceptual_detection(found_bugs, gt_bugs, task)
        
        return {
            "task_id": task.get("id", "unknown"),
            "level": "L2_perceptual",
            "domain": "perceptual",
            "category": task.get("category", "unknown"),
            "bug_type": task.get("bug_type", "unknown"),
            "severity": task.get("severity", "unknown"),
            "model": self.model,
            "num_planted_bugs": len(gt_bugs),
            "num_bugs_found": len(found_bugs),
            "bugs_found": found_bugs,
            "ground_truth_bugs": gt_bugs,
            "detection_rate": detection_result["detection_rate"],
            "false_alarm_count": detection_result["false_alarms"],
            "matched_bugs": detection_result["matched"],
            "raw_response": parsed,
            "timestamp": datetime.now().isoformat()
        }
    
    def _score_perceptual_detection(self, found: list, ground_truth: list, task: dict) -> dict:
        """Score how many planted bugs were detected.
        Uses keyword matching between found bugs and ground truth descriptions.
        """
        matched = []
        unmatched_gt = list(range(len(ground_truth)))
        
        # Key terms from each ground truth bug for matching
        for found_bug in found:
            found_lower = found_bug.lower()
            best_match = -1
            best_score = 0
            
            for gt_idx in unmatched_gt:
                gt_lower = ground_truth[gt_idx].lower()
                # Extract key terms from ground truth
                gt_terms = set(gt_lower.split())
                found_terms = set(found_lower.split())
                overlap = len(gt_terms & found_terms)
                
                # Also check for semantic keywords from the bug type
                bug_type = task.get("bug_type", "").lower()
                category = task.get("category", "").lower()
                
                # Boost score if category-specific keywords match
                category_keywords = {
                    "image_sizing": ["stretch", "aspect", "ratio", "distort", "size", "height", "width", "tiny", "small", "image"],
                    "text_contrast": ["contrast", "readabl", "color", "text", "background", "invisible", "unreadable"],
                    "button_issues": ["button", "click", "disabled", "pointer", "unclickable", "opacity"],
                    "layout_overflow": ["overflow", "truncat", "wrap", "break", "horizontal", "scroll"],
                    "missing_elements": ["missing", "empty", "hidden", "display:none", "invisible", "NaN", "duplicate", "password"],
                    "alignment_spacing": ["align", "margin", "spacing", "misalign", "swap", "color", "mismatch", "progress"],
                    "z_index_overlap": ["z-index", "behind", "overlap", "hidden", "modal", "dropdown"],
                    "responsive_issues": ["responsive", "mobile", "breakpoint", "media", "white", "invisible"],
                }
                
                bonus = 0
                for kw in category_keywords.get(category, []):
                    if kw in found_lower and kw in gt_lower:
                        bonus += 3
                
                score = overlap + bonus
                if score > best_score:
                    best_score = score
                    best_match = gt_idx
            
            if best_match >= 0 and best_score >= 3:
                matched.append((found_bug, ground_truth[best_match]))
                unmatched_gt.remove(best_match)
        
        num_matched = len(matched)
        detection_rate = num_matched / len(ground_truth) if ground_truth else 0
        false_alarms = max(0, len(found) - num_matched)
        
        return {
            "matched": num_matched,
            "detection_rate": round(detection_rate, 4),
            "false_alarms": false_alarms
        }
    
    # ============================================================
    # Level 3: Consistency Validation
    # ============================================================
    
    def evaluate_consistency_task(self, task: dict) -> dict:
        """Evaluate if the model can detect planted contradictions."""
        artifact_parts = task.get("artifact_parts", {})
        description = task.get("description", "")
        
        # Format artifact parts for the prompt
        parts_formatted = ""
        for part_name, part_content in artifact_parts.items():
            display_name = part_name.replace("_", " ").title()
            parts_formatted += f"--- {display_name} ---\n{part_content}\n\n"
        
        detect_prompt = CONSISTENCY_DETECT_PROMPT.format(
            description=description,
            artifact_parts_formatted=parts_formatted
        )
        
        response = self.call_llm(detect_prompt, system="You are an expert document reviewer and quality assurance specialist.")
        parsed = self.parse_json_response(response)
        
        # Ground truth
        gt_contradictions = task.get("ground_truth", [])
        found_contradictions = parsed.get("contradictions_found", [])
        
        # Score detection
        detection_result = self._score_consistency_detection(found_contradictions, gt_contradictions)
        
        return {
            "task_id": task.get("id", "unknown"),
            "level": "L3_consistency",
            "domain": "consistency",
            "category": task.get("category", "unknown"),
            "model": self.model,
            "num_planted_contradictions": len(gt_contradictions),
            "num_contradictions_found": len(found_contradictions),
            "contradictions_found": found_contradictions,
            "ground_truth_contradictions": gt_contradictions,
            "detection_rate": detection_result["detection_rate"],
            "precision": detection_result["precision"],
            "false_alarm_count": detection_result["false_alarms"],
            "matched_contradictions": detection_result["matched"],
            "raw_response": parsed,
            "timestamp": datetime.now().isoformat()
        }
    
    def _score_consistency_detection(self, found: list, ground_truth: list) -> dict:
        """Score how many planted contradictions were detected."""
        matched = []
        unmatched_gt = list(range(len(ground_truth)))
        
        for found_item in found:
            found_lower = found_item.lower()
            best_match = -1
            best_score = 0
            
            for gt_idx in unmatched_gt:
                gt_lower = ground_truth[gt_idx].lower()
                
                # Extract numbers from both strings for comparison
                found_nums = set(re.findall(r'\d+\.?\d*', found_lower))
                gt_nums = set(re.findall(r'\d+\.?\d*', gt_lower))
                num_overlap = len(found_nums & gt_nums)
                
                # Word overlap
                gt_terms = set(re.findall(r'\w+', gt_lower))
                found_terms = set(re.findall(r'\w+', found_lower))
                word_overlap = len(gt_terms & found_terms)
                
                score = word_overlap + num_overlap * 5  # Numbers are strong signals
                
                if score > best_score:
                    best_score = score
                    best_match = gt_idx
            
            if best_match >= 0 and best_score >= 5:
                matched.append((found_item, ground_truth[best_match]))
                unmatched_gt.remove(best_match)
        
        num_matched = len(matched)
        detection_rate = num_matched / len(ground_truth) if ground_truth else 0
        precision = num_matched / len(found) if found else 0
        false_alarms = max(0, len(found) - num_matched)
        
        return {
            "matched": num_matched,
            "detection_rate": round(detection_rate, 4),
            "precision": round(precision, 4),
            "false_alarms": false_alarms
        }
    
    # ============================================================
    # Outcome Classification (Level 1)
    # ============================================================
    def _classify_outcome(self, model_says_pass: bool, actual_pass: bool) -> str:
        if model_says_pass and actual_pass:
            return "TRUE_POSITIVE"
        elif not model_says_pass and not actual_pass:
            return "TRUE_NEGATIVE"
        elif model_says_pass and not actual_pass:
            return "FALSE_POSITIVE"
        else:
            return "FALSE_NEGATIVE"
    
    # ============================================================
    # Main Evaluation Loop
    # ============================================================
    def run_evaluation(self, domain: str, num_tasks: Optional[int] = None) -> list:
        """Run evaluation on a specific domain."""
        tasks = self._load_tasks(domain)
        if num_tasks:
            tasks = tasks[:num_tasks]
        
        results = []
        total = len(tasks)
        
        level_name = "L1-Logical" if domain in LEVEL1_DOMAINS else "L2-Perceptual" if domain in LEVEL2_DOMAINS else "L3-Consistency"
        
        print(f"\n{'='*60}")
        print(f"E²-Bench Evaluation: [{level_name}] {domain}")
        print(f"Model: {self.model}")
        print(f"Tasks: {total}")
        print(f"{'='*60}\n")
        
        for i, task in enumerate(tasks):
            task_id = task.get("task_id", task.get("id", "unknown"))
            print(f"[{i+1}/{total}] {task_id}...", end=" ", flush=True)
            
            if domain == "code":
                result = self.evaluate_code_task(task)
            elif domain == "data_analysis":
                result = self.evaluate_data_task(task)
            elif domain == "reasoning":
                result = self.evaluate_reasoning_task(task)
            elif domain == "perceptual":
                result = self.evaluate_perceptual_task(task)
            elif domain == "consistency":
                result = self.evaluate_consistency_task(task)
            else:
                print(f"Unknown domain: {domain}")
                continue
            
            results.append(result)
            
            # Print result based on level
            if domain in LEVEL1_DOMAINS:
                print(f"→ Model: {result['model_decision']}, Actual: {result['actual_result']}, Outcome: {result['outcome']}")
            elif domain == "perceptual":
                print(f"→ Found {result['num_bugs_found']}/{result['num_planted_bugs']} bugs (detection rate: {result['detection_rate']:.0%})")
            elif domain == "consistency":
                print(f"→ Found {result['num_contradictions_found']}/{result['num_planted_contradictions']} contradictions (detection rate: {result['detection_rate']:.0%})")
        
        return results
    
    def _load_tasks(self, domain: str) -> list:
        """Load tasks from the eval set."""
        domain_map = {
            "code": "code_generation",
            "data_analysis": "data_analysis",
            "reasoning": "logical_reasoning",
            "perceptual": "perceptual_validation",
            "consistency": "consistency_validation"
        }
        path = os.path.join(EVAL_SET_DIR, domain_map[domain], "tasks.json")
        with open(path) as f:
            return json.load(f)
    
    def compute_metrics(self, results: list, domain: str) -> dict:
        """Compute E²-Bench metrics from evaluation results."""
        total = len(results)
        if total == 0:
            return {}
        
        if domain in LEVEL1_DOMAINS:
            return self._compute_level1_metrics(results)
        elif domain == "perceptual":
            return self._compute_level2_metrics(results)
        elif domain == "consistency":
            return self._compute_level3_metrics(results)
        return {}
    
    def _compute_level1_metrics(self, results: list) -> dict:
        """Compute Level 1 (Logical Validation) metrics."""
        total = len(results)
        tp = sum(1 for r in results if r["outcome"] == "TRUE_POSITIVE")
        tn = sum(1 for r in results if r["outcome"] == "TRUE_NEGATIVE")
        fp = sum(1 for r in results if r["outcome"] == "FALSE_POSITIVE")
        fn = sum(1 for r in results if r["outcome"] == "FALSE_NEGATIVE")
        
        sva = (tp + tn) / total if total > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
        task_pass_rate = (tp + fn) / total if total > 0 else 0
        
        return {
            "level": "L1_logical",
            "model": results[0]["model"],
            "domain": results[0]["domain"],
            "total_tasks": total,
            "true_positives": tp,
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "self_validation_accuracy": round(sva, 4),
            "false_positive_rate": round(fpr, 4),
            "false_negative_rate": round(fnr, 4),
            "task_pass_rate": round(task_pass_rate, 4),
        }
    
    def _compute_level2_metrics(self, results: list) -> dict:
        """Compute Level 2 (Perceptual Validation) metrics."""
        total = len(results)
        total_planted = sum(r["num_planted_bugs"] for r in results)
        total_found = sum(r["num_bugs_found"] for r in results)
        total_matched = sum(r["matched_bugs"] for r in results)
        total_false_alarms = sum(r["false_alarm_count"] for r in results)
        
        avg_detection_rate = sum(r["detection_rate"] for r in results) / total if total > 0 else 0
        overall_recall = total_matched / total_planted if total_planted > 0 else 0
        overall_precision = total_matched / total_found if total_found > 0 else 0
        
        # Breakdown by category
        by_category = {}
        for r in results:
            cat = r["category"]
            if cat not in by_category:
                by_category[cat] = {"total": 0, "planted": 0, "matched": 0, "found": 0}
            by_category[cat]["total"] += 1
            by_category[cat]["planted"] += r["num_planted_bugs"]
            by_category[cat]["matched"] += r["matched_bugs"]
            by_category[cat]["found"] += r["num_bugs_found"]
        
        for cat in by_category:
            d = by_category[cat]
            d["detection_rate"] = round(d["matched"] / d["planted"], 4) if d["planted"] > 0 else 0
        
        return {
            "level": "L2_perceptual",
            "model": results[0]["model"],
            "domain": "perceptual",
            "total_tasks": total,
            "total_planted_bugs": total_planted,
            "total_bugs_found": total_found,
            "total_bugs_matched": total_matched,
            "total_false_alarms": total_false_alarms,
            "avg_detection_rate": round(avg_detection_rate, 4),
            "overall_recall": round(overall_recall, 4),
            "overall_precision": round(overall_precision, 4),
            "by_category": by_category,
        }
    
    def _compute_level3_metrics(self, results: list) -> dict:
        """Compute Level 3 (Consistency Validation) metrics."""
        total = len(results)
        total_planted = sum(r["num_planted_contradictions"] for r in results)
        total_found = sum(r["num_contradictions_found"] for r in results)
        total_matched = sum(r["matched_contradictions"] for r in results)
        total_false_alarms = sum(r["false_alarm_count"] for r in results)
        
        avg_detection_rate = sum(r["detection_rate"] for r in results) / total if total > 0 else 0
        overall_recall = total_matched / total_planted if total_planted > 0 else 0
        overall_precision = total_matched / total_found if total_found > 0 else 0
        
        # Breakdown by category
        by_category = {}
        for r in results:
            cat = r["category"]
            if cat not in by_category:
                by_category[cat] = {"total": 0, "planted": 0, "matched": 0, "found": 0}
            by_category[cat]["total"] += 1
            by_category[cat]["planted"] += r["num_planted_contradictions"]
            by_category[cat]["matched"] += r["matched_contradictions"]
            by_category[cat]["found"] += r["num_contradictions_found"]
        
        for cat in by_category:
            d = by_category[cat]
            d["detection_rate"] = round(d["matched"] / d["planted"], 4) if d["planted"] > 0 else 0
        
        return {
            "level": "L3_consistency",
            "model": results[0]["model"],
            "domain": "consistency",
            "total_tasks": total,
            "total_planted_contradictions": total_planted,
            "total_contradictions_found": total_found,
            "total_contradictions_matched": total_matched,
            "total_false_alarms": total_false_alarms,
            "avg_detection_rate": round(avg_detection_rate, 4),
            "overall_recall": round(overall_recall, 4),
            "overall_precision": round(overall_precision, 4),
            "by_category": by_category,
        }
    
    def save_results(self, results: list, metrics: dict, domain: str):
        """Save results and metrics to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_safe = self.model.replace("/", "_").replace(":", "_")
        
        results_path = os.path.join(self.output_dir, f"{model_safe}_{domain}_{timestamp}_results.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        
        metrics_path = os.path.join(self.output_dir, f"{model_safe}_{domain}_{timestamp}_metrics.json")
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)
        
        print(f"\nResults saved to: {results_path}")
        print(f"Metrics saved to: {metrics_path}")
        return results_path, metrics_path
    
    def print_summary(self, metrics: dict, domain: str):
        """Print a human-readable summary of the metrics."""
        print(f"\n{'='*60}")
        print(f"SUMMARY: {domain} ({metrics.get('model', 'unknown')})")
        print(f"{'='*60}")
        
        if domain in LEVEL1_DOMAINS:
            print(f"  Level: L1 - Logical Validation")
            print(f"  Self-Validation Accuracy (SVA): {metrics.get('self_validation_accuracy', 0):.1%}")
            print(f"  False Positive Rate (FPR):      {metrics.get('false_positive_rate', 0):.1%}")
            print(f"  False Negative Rate (FNR):      {metrics.get('false_negative_rate', 0):.1%}")
            print(f"  Task Pass Rate:                 {metrics.get('task_pass_rate', 0):.1%}")
            print(f"  TP={metrics.get('true_positives',0)} TN={metrics.get('true_negatives',0)} FP={metrics.get('false_positives',0)} FN={metrics.get('false_negatives',0)}")
        
        elif domain == "perceptual":
            print(f"  Level: L2 - Perceptual Validation")
            print(f"  Avg Detection Rate:    {metrics.get('avg_detection_rate', 0):.1%}")
            print(f"  Overall Recall:        {metrics.get('overall_recall', 0):.1%}")
            print(f"  Overall Precision:     {metrics.get('overall_precision', 0):.1%}")
            print(f"  Total Planted Bugs:    {metrics.get('total_planted_bugs', 0)}")
            print(f"  Total Bugs Matched:    {metrics.get('total_bugs_matched', 0)}")
            print(f"  False Alarms:          {metrics.get('total_false_alarms', 0)}")
            if "by_category" in metrics:
                print(f"\n  By Category:")
                for cat, data in metrics["by_category"].items():
                    print(f"    {cat}: {data['matched']}/{data['planted']} detected ({data['detection_rate']:.0%})")
        
        elif domain == "consistency":
            print(f"  Level: L3 - Consistency Validation")
            print(f"  Avg Detection Rate:    {metrics.get('avg_detection_rate', 0):.1%}")
            print(f"  Overall Recall:        {metrics.get('overall_recall', 0):.1%}")
            print(f"  Overall Precision:     {metrics.get('overall_precision', 0):.1%}")
            print(f"  Total Planted:         {metrics.get('total_planted_contradictions', 0)}")
            print(f"  Total Matched:         {metrics.get('total_contradictions_matched', 0)}")
            print(f"  False Alarms:          {metrics.get('total_false_alarms', 0)}")
            if "by_category" in metrics:
                print(f"\n  By Category:")
                for cat, data in metrics["by_category"].items():
                    print(f"    {cat}: {data['matched']}/{data['planted']} detected ({data['detection_rate']:.0%})")


# ============================================================
# CLI Entry Point
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="E²-Bench: Eval of Eval Benchmark")
    parser.add_argument("--model", type=str, default="gpt-4.1-mini", help="Model to evaluate")
    parser.add_argument("--domain", type=str, default="code",
                        choices=ALL_DOMAINS + ["all", "level1", "level2", "level3"])
    parser.add_argument("--num_tasks", type=int, default=None, help="Number of tasks (default: all)")
    parser.add_argument("--output", type=str, default="results", help="Output directory")
    args = parser.parse_args()
    
    evaluator = E2BenchEvaluator(model=args.model, output_dir=args.output)
    
    if args.domain == "all":
        domains = ALL_DOMAINS
    elif args.domain == "level1":
        domains = LEVEL1_DOMAINS
    elif args.domain == "level2":
        domains = LEVEL2_DOMAINS
    elif args.domain == "level3":
        domains = LEVEL3_DOMAINS
    else:
        domains = [args.domain]
    
    all_metrics = {}
    for domain in domains:
        results = evaluator.run_evaluation(domain, args.num_tasks)
        metrics = evaluator.compute_metrics(results, domain)
        evaluator.save_results(results, metrics, domain)
        evaluator.print_summary(metrics, domain)
        all_metrics[domain] = metrics
    
    if len(domains) > 1:
        combined_path = os.path.join(args.output, f"{args.model.replace('/','_')}_combined_metrics.json")
        with open(combined_path, "w") as f:
            json.dump(all_metrics, f, indent=2)
        print(f"\nCombined metrics saved to: {combined_path}")

if __name__ == "__main__":
    main()
