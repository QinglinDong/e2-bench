"""
E²-Bench: Generate Logical Reasoning eval tasks.
Each task has: task_id, description, ground_truth_answer, difficulty, verification_steps
Covers: Game of 24, constraint satisfaction, logic puzzles, math reasoning
"""
import json
import os
import random
import itertools
from openai import OpenAI

client = OpenAI()

# ============================================================
# PART 1: Deterministically generated Game of 24 puzzles (50)
# ============================================================
def solve_24(nums):
    """Find all ways to make 24 from 4 numbers using +, -, *, /"""
    if len(nums) == 1:
        if abs(nums[0] - 24) < 1e-9:
            return True
        return False
    
    for i in range(len(nums)):
        for j in range(len(nums)):
            if i == j:
                continue
            remaining = [nums[k] for k in range(len(nums)) if k != i and k != j]
            a, b = nums[i], nums[j]
            for op in ['+', '-', '*', '/']:
                if op == '+': result = a + b
                elif op == '-': result = a - b
                elif op == '*': result = a * b
                elif op == '/':
                    if b == 0: continue
                    result = a / b
                if solve_24(remaining + [result]):
                    return True
    return False

def find_24_expression(nums):
    """Find an expression that makes 24"""
    ops = ['+', '-', '*', '/']
    for perm in itertools.permutations(nums):
        a, b, c, d = perm
        for o1 in ops:
            for o2 in ops:
                for o3 in ops:
                    # Try different parenthesizations
                    expressions = [
                        f"(({a} {o1} {b}) {o2} {c}) {o3} {d}",
                        f"({a} {o1} ({b} {o2} {c})) {o3} {d}",
                        f"({a} {o1} {b}) {o2} ({c} {o3} {d})",
                        f"{a} {o1} (({b} {o2} {c}) {o3} {d})",
                        f"{a} {o1} ({b} {o2} ({c} {o3} {d}))",
                    ]
                    for expr in expressions:
                        try:
                            if abs(eval(expr) - 24) < 1e-9:
                                return expr
                        except:
                            pass
    return None

def generate_game_of_24_tasks(n=50):
    random.seed(42)
    tasks = []
    solvable_count = 0
    unsolvable_count = 0
    
    # Generate a mix of solvable and unsolvable
    attempts = 0
    while len(tasks) < n and attempts < 5000:
        attempts += 1
        nums = [random.randint(1, 13) for _ in range(4)]
        is_solvable = solve_24([float(x) for x in nums])
        
        if is_solvable and solvable_count < 35:
            expr = find_24_expression(nums)
            tasks.append({
                "task_id": f"game24_{len(tasks)+1:03d}",
                "type": "game_of_24",
                "description": f"Using the numbers {nums[0]}, {nums[1]}, {nums[2]}, and {nums[3]}, and the operations +, -, *, /, make the number 24. Each number must be used exactly once. Is it possible? If yes, provide the expression.",
                "numbers": nums,
                "ground_truth_solvable": True,
                "ground_truth_answer": f"Yes. Example: {expr}" if expr else "Yes (expression exists)",
                "difficulty": "medium",
                "category": "game_of_24"
            })
            solvable_count += 1
        elif not is_solvable and unsolvable_count < 15:
            tasks.append({
                "task_id": f"game24_{len(tasks)+1:03d}",
                "type": "game_of_24",
                "description": f"Using the numbers {nums[0]}, {nums[1]}, {nums[2]}, and {nums[3]}, and the operations +, -, *, /, make the number 24. Each number must be used exactly once. Is it possible? If yes, provide the expression.",
                "numbers": nums,
                "ground_truth_solvable": False,
                "ground_truth_answer": "No, it is not possible to make 24 with these numbers.",
                "difficulty": "hard",
                "category": "game_of_24"
            })
            unsolvable_count += 1
    
    return tasks

# ============================================================
# PART 2: LLM-generated logic puzzles (100)
# ============================================================
LOGIC_CATEGORIES = [
    ("constraint_satisfaction", 25, [
        "A scheduling puzzle: 4 meetings must be assigned to 4 time slots with constraints on who cannot meet at the same time",
        "A seating arrangement: 6 people around a circular table with adjacency constraints",
        "A map coloring problem: color 5 regions with 3 colors such that no adjacent regions share a color",
        "A task assignment: 4 workers to 4 tasks where each worker has different skill levels and we want to minimize total cost",
        "A Sudoku-like 4x4 grid puzzle with given clues",
        "A scheduling puzzle: 5 courses must be assigned to 3 rooms across 4 time slots with no conflicts",
        "A tournament bracket: determine the winner given match results and seeding rules",
        "A resource allocation: distribute 100 units among 4 projects to maximize total value with constraints",
        "A shift scheduling: assign 6 nurses to 3 shifts over 2 days with rest constraints",
        "A bin packing: fit items of sizes 3,5,7,2,8,4 into bins of capacity 10 using minimum bins",
        "A job shop scheduling: 3 jobs each with 2 operations on 2 machines to minimize makespan",
        "A classroom assignment: 8 classes to 4 rooms with capacity and equipment constraints",
        "A diet planning: select foods to meet nutritional requirements at minimum cost",
        "A vehicle routing: find the shortest route visiting 5 cities and returning to start",
        "A warehouse layout: assign 6 products to 6 locations minimizing total retrieval distance",
        "A exam timetabling: schedule 6 exams in 3 days where students taking common exams cannot have conflicts",
        "A frequency assignment: assign 4 frequencies to 5 radio towers with interference constraints",
        "A sports league scheduling: create a round-robin schedule for 6 teams over 5 weeks",
        "A project scheduling with dependencies: find the critical path for 8 tasks",
        "A knapsack selection: choose items with given weights and values to maximize value within weight limit 15",
        "A graph coloring: determine the chromatic number of a specific small graph",
        "A Latin square completion: fill in missing values in a partially completed 4x4 Latin square",
        "A cryptarithmetic puzzle: find digits where SEND + MORE = MONEY",
        "A logic grid puzzle: match 4 people to their pets, colors, and houses from clues",
        "A set cover: find the minimum number of sets from a collection that covers all elements",
    ]),
    ("deductive_reasoning", 25, [
        "Knights and Knaves: 3 people make statements, determine who is a knight (always tells truth) and who is a knave (always lies)",
        "A murder mystery logic puzzle: given 5 clues, determine who committed the crime",
        "Syllogism evaluation: given two premises, determine if the conclusion is valid",
        "A truth table puzzle: determine the truth value of a compound logical expression",
        "A river crossing puzzle: farmer, fox, chicken, and grain must cross with constraints",
        "A hat puzzle: 3 people wearing hats, determine what color hat you're wearing from others' responses",
        "A birthday paradox calculation: what's the probability of shared birthday in a group of 23",
        "A Monty Hall problem variant: should you switch doors given specific conditions",
        "A prisoners and hats puzzle: 4 prisoners in a line, determine the optimal strategy",
        "A weighing puzzle: find the counterfeit coin among 8 using a balance scale in minimum weighings",
        "A logic puzzle: from 5 statements, exactly 2 are true, determine which ones",
        "A zebra puzzle variant: 4 houses, 4 nationalities, 4 drinks, 4 pets with clues",
        "A truth-teller and liar puzzle: ask one question to determine which door leads to freedom",
        "A deduction puzzle: given a sequence of events and alibis, determine the timeline",
        "A card puzzle: determine the hidden card from statements about a 5-card hand",
        "A family relationship puzzle: determine relationships from 6 clues about a family",
        "A code-breaking puzzle: deduce a 4-digit code from 5 guesses with feedback",
        "A island of truth puzzle: navigate between villages of truth-tellers and liars",
        "A age puzzle: determine ages of 3 people from relationship clues",
        "A ranking puzzle: determine the complete ranking of 5 items from pairwise comparisons",
        "A box puzzle: 3 boxes labeled incorrectly, determine contents with minimum openings",
        "A clock puzzle: at what time do the hour and minute hands overlap after 12:00",
        "A probability puzzle: drawing balls from urns with replacement",
        "A pigeonhole principle application: prove a specific combinatorial statement",
        "A logical paradox analysis: determine if a given statement is self-consistent",
    ]),
    ("mathematical_reasoning", 25, [
        "Prove that the sum of first n odd numbers equals n squared, then verify for n=10",
        "Find the remainder when 2^100 is divided by 7",
        "Determine how many integers from 1 to 1000 are divisible by 3 or 5 but not both",
        "Calculate the number of ways to arrange the letters in MISSISSIPPI",
        "Find the last two digits of 7^2026",
        "Determine the minimum number of handshakes if 10 people each shake hands with exactly 3 others",
        "Calculate the expected number of coin flips to get 3 consecutive heads",
        "Find the number of paths from (0,0) to (4,4) on a grid moving only right or up",
        "Determine if 2^67 - 1 is prime (Mersenne prime check)",
        "Calculate the sum of all proper divisors of 360",
        "Find the number of trailing zeros in 100 factorial",
        "Determine the smallest n such that n! > 10^100",
        "Calculate the number of derangements of 6 elements",
        "Find the GCD of 1071 and 462 using the Euclidean algorithm showing all steps",
        "Determine the number of distinct binary search trees with 5 nodes",
        "Calculate the probability of getting a full house in a 5-card poker hand",
        "Find the number of integer solutions to x1+x2+x3+x4=20 where each xi>=0",
        "Determine the value of the continued fraction [1;1,1,1,...] (infinite)",
        "Calculate the sum of the series 1/1 + 1/3 + 1/6 + 1/10 + ... + 1/55",
        "Find the number of ways to partition 10 into positive integers",
        "Determine the chromatic polynomial of a cycle graph C5 evaluated at k=3",
        "Calculate the determinant of a specific 4x4 matrix",
        "Find the eigenvalues of the matrix [[2,1],[1,2]]",
        "Determine the number of surjective functions from a 5-element set to a 3-element set",
        "Calculate the volume of the region bounded by x^2+y^2+z^2<=1 and z>=0",
    ]),
    ("algorithmic_thinking", 25, [
        "Trace through bubble sort on [5,3,8,1,2] and count the number of swaps",
        "Determine the output of a specific recursive function call",
        "Find the time complexity of a given nested loop structure",
        "Trace through Dijkstra's algorithm on a small weighted graph",
        "Determine what a specific piece of pseudocode computes",
        "Find the minimum number of operations to transform string A to string B",
        "Trace through a binary search on a sorted array and count comparisons",
        "Determine the output of a BFS traversal starting from a specific node",
        "Find the optimal strategy for a specific two-player game",
        "Trace through quicksort partition on [7,2,1,6,8,5,3,4] with pivot=4",
        "Determine the maximum flow in a specific small network",
        "Find the longest common subsequence of two specific strings",
        "Trace through an inorder traversal of a specific binary tree",
        "Determine the number of comparisons in merge sort for 8 elements",
        "Find the shortest path in a specific weighted graph using Bellman-Ford",
        "Trace through a hash table insertion sequence with linear probing",
        "Determine the amortized cost of n operations on a dynamic array",
        "Find the minimum spanning tree weight of a specific graph",
        "Trace through the KMP failure function computation for a specific pattern",
        "Determine the output of a specific dynamic programming table",
        "Find the number of strongly connected components in a specific directed graph",
        "Trace through Huffman coding for a specific frequency table",
        "Determine the result of applying a specific sorting network to an input",
        "Find the maximum matching in a specific bipartite graph",
        "Trace through the execution of a specific finite automaton on an input string",
    ]),
]

LOGIC_SYSTEM_PROMPT = """You are an expert puzzle designer creating logic and reasoning tasks for a benchmark.
Given a task hint, you must produce a JSON object with:
1. "task_id": a unique snake_case identifier
2. "description": the complete puzzle statement with all necessary information (3-8 sentences). Must be self-contained and unambiguous.
3. "ground_truth_answer": the exact correct answer. Must be specific and verifiable.
4. "verification_steps": step-by-step logical reasoning that proves the answer is correct (3-8 steps)
5. "difficulty": one of "easy", "medium", "hard"
6. "answer_type": one of "numeric", "boolean", "choice", "expression", "list"

IMPORTANT:
- The puzzle MUST have exactly ONE correct answer
- The verification_steps MUST logically prove the answer
- Include all necessary data in the description (numbers, constraints, relationships)
- For mathematical problems, show the exact computation
- Output valid JSON only, no markdown formatting"""

def generate_logic_task(category: str, task_hint: str, idx: int) -> dict:
    prompt = f"""Category: {category}
Task hint: {task_hint}
Task index: {idx}

Generate a complete logic/reasoning benchmark task. The puzzle must have exactly one correct answer that can be verified step-by-step."""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": LOGIC_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        task = json.loads(response.choices[0].message.content)
        task["category"] = category
        task["task_index"] = idx
        return task
    except Exception as e:
        print(f"Error generating task {idx} ({task_hint}): {e}")
        return None

def main():
    # Part 1: Game of 24 (deterministic)
    print("=== Generating Game of 24 tasks (deterministic) ===")
    game24_tasks = generate_game_of_24_tasks(50)
    print(f"  Generated {len(game24_tasks)} Game of 24 tasks")
    
    # Part 2: LLM-generated logic puzzles
    all_logic_tasks = []
    task_idx = 0
    
    for category, count, hints in LOGIC_CATEGORIES:
        print(f"\n=== Generating {count} tasks for category: {category} ===")
        for i, hint in enumerate(hints[:count]):
            task_idx += 1
            print(f"  [{task_idx}/100] {hint[:60]}...")
            task = generate_logic_task(category, hint, task_idx)
            if task:
                all_logic_tasks.append(task)
    
    # Combine
    all_tasks = game24_tasks + all_logic_tasks
    
    output_path = "/home/ubuntu/e2_bench/eval_set/logical_reasoning/tasks.json"
    with open(output_path, "w") as f:
        json.dump(all_tasks, f, indent=2)
    
    print(f"\nGenerated {len(all_tasks)} total reasoning tasks -> {output_path}")

if __name__ == "__main__":
    main()
