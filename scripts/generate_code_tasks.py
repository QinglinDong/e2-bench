"""
E²-Bench: Generate Code Generation eval tasks.
Each task has: task_id, description, function_signature, difficulty, hidden_tests, canonical_solution
"""
import json
import os
from openai import OpenAI

client = OpenAI()

CATEGORIES = [
    ("string_manipulation", 25, [
        "reverse words in a string preserving spaces",
        "check if two strings are anagrams ignoring case and spaces",
        "find the longest palindromic substring",
        "compress a string using run-length encoding",
        "decode a run-length encoded string",
        "check if a string matches a simplified regex with . and *",
        "find all permutations of a string without duplicates",
        "convert a Roman numeral string to an integer",
        "convert an integer to a Roman numeral string",
        "implement a basic Caesar cipher encoder and decoder",
        "find the minimum window substring containing all characters of a target",
        "group anagrams from a list of strings",
        "check if a string of parentheses brackets and braces is balanced",
        "find the longest common prefix among a list of strings",
        "implement string multiplication for two large number strings",
        "count distinct subsequences of a pattern in a text",
        "interleave two strings alternating characters",
        "remove all adjacent duplicates in a string repeatedly until stable",
        "check if one string is a rotation of another",
        "find the first non-repeating character in a string",
        "implement wildcard pattern matching with ? and *",
        "encode a string using base64 without libraries",
        "decode a base64 encoded string without libraries",
        "find the longest substring without repeating characters",
        "validate if a string is a valid IPv4 address",
    ]),
    ("array_and_sorting", 25, [
        "merge two sorted arrays in-place",
        "find the kth largest element in an unsorted array",
        "find all pairs in an array that sum to a target value",
        "implement quicksort and return the sorted array",
        "find the maximum subarray sum (Kadane's algorithm)",
        "rotate an array to the right by k positions",
        "find the majority element that appears more than n/2 times",
        "merge overlapping intervals",
        "find the missing number in an array of 0 to n",
        "implement binary search on a sorted array",
        "find the median of two sorted arrays",
        "sort an array of 0s 1s and 2s in-place (Dutch National Flag)",
        "find the longest increasing subsequence length",
        "trap rainwater given elevation map as array",
        "find the product of array except self without division",
        "find the next permutation of an array of integers",
        "find the smallest positive integer missing from an unsorted array",
        "count inversions in an array using merge sort",
        "find the maximum product subarray",
        "implement a function to partition array around a pivot",
        "find three numbers in array that sum closest to target",
        "find the peak element in an array",
        "remove duplicates from sorted array in-place return new length",
        "find the contiguous subarray of size k with maximum average",
        "implement counting sort for non-negative integers",
    ]),
    ("linked_list_and_tree", 25, [
        "reverse a singly linked list",
        "detect a cycle in a linked list",
        "merge two sorted linked lists",
        "find the middle node of a linked list",
        "remove the nth node from end of linked list",
        "check if a linked list is a palindrome",
        "flatten a multilevel doubly linked list",
        "add two numbers represented as linked lists",
        "find the intersection node of two linked lists",
        "implement LRU cache with get and put operations",
        "validate a binary search tree",
        "find the lowest common ancestor of two nodes in a BST",
        "serialize and deserialize a binary tree",
        "find the maximum depth of a binary tree",
        "check if a binary tree is symmetric",
        "convert a sorted array to a balanced BST",
        "find all root-to-leaf paths in a binary tree",
        "invert a binary tree",
        "find the diameter of a binary tree",
        "implement level-order traversal of a binary tree",
        "find the kth smallest element in a BST",
        "construct binary tree from preorder and inorder traversal",
        "check if two binary trees are identical",
        "find the right side view of a binary tree",
        "count the number of nodes in a complete binary tree",
    ]),
    ("dynamic_programming", 25, [
        "compute the nth Fibonacci number efficiently",
        "find the minimum number of coins to make a given amount",
        "find the length of the longest common subsequence of two strings",
        "count the number of unique paths in an m x n grid",
        "solve the 0/1 knapsack problem",
        "find the minimum edit distance between two strings",
        "find the longest palindromic subsequence",
        "count the number of ways to climb n stairs taking 1 or 2 steps",
        "find the maximum profit from at most k stock transactions",
        "partition a set into two subsets with minimum difference",
        "find the minimum path sum in a grid from top-left to bottom-right",
        "count the number of distinct ways to decode a digit string to letters",
        "find the length of the longest increasing subsequence",
        "determine if a string can be segmented into dictionary words",
        "find the maximum length of a subarray with sum equal to k",
        "compute the minimum number of matrix chain multiplications",
        "find the maximum sum of non-adjacent elements in an array",
        "count palindromic substrings in a string",
        "solve the egg drop problem with n eggs and k floors",
        "find the minimum number of jumps to reach the end of array",
        "find the longest common substring of two strings",
        "compute the number of ways to tile a 2xN board with 2x1 tiles",
        "find the maximum profit from rod cutting",
        "determine if a target sum can be formed from array elements",
        "find the shortest common supersequence of two strings",
    ]),
    ("graph_algorithms", 25, [
        "implement BFS traversal of a graph from a source node",
        "implement DFS traversal of a graph from a source node",
        "detect a cycle in a directed graph",
        "detect a cycle in an undirected graph",
        "find the shortest path in an unweighted graph using BFS",
        "implement Dijkstra's shortest path algorithm",
        "find the number of connected components in an undirected graph",
        "determine if a graph is bipartite",
        "find the topological sort of a directed acyclic graph",
        "find all bridges in an undirected graph",
        "find the number of islands in a 2D grid",
        "clone a graph given a reference to a node",
        "find the minimum spanning tree using Kruskal's algorithm",
        "find if there is a path between two nodes in a graph",
        "solve the course schedule problem (detect if all courses can be finished)",
        "find the shortest path in a grid with obstacles",
        "implement Floyd-Warshall all-pairs shortest path",
        "find strongly connected components using Tarjan's algorithm",
        "find the cheapest flight within k stops",
        "solve word ladder: find shortest transformation sequence",
        "find the critical connections in a network",
        "implement union-find with path compression and union by rank",
        "find the longest path in a DAG",
        "solve the maze problem using backtracking",
        "determine if a graph can be colored with at most k colors",
    ]),
    ("hash_map_and_set", 20, [
        "find two numbers in array that add up to target using hash map",
        "find the first duplicate in an array",
        "check if an array contains duplicate elements within k distance",
        "group people by their birth year from a list of (name, year) tuples",
        "find the longest consecutive sequence in an unsorted array",
        "implement a frequency counter and return top k frequent elements",
        "check if two strings are isomorphic",
        "find all four-number combinations that sum to target",
        "implement a hash map from scratch with get put and remove",
        "find the intersection of two arrays",
        "find the union of two arrays without duplicates",
        "count subarrays with sum equal to k",
        "find the smallest subarray with sum greater than or equal to target",
        "check if a Sudoku board is valid",
        "find all duplicate subtrees in a binary tree",
        "implement a multiset that supports add remove and count",
        "find the longest substring with at most k distinct characters",
        "design a data structure for insert delete and getRandom in O(1)",
        "find the minimum index sum of two lists of favorite restaurants",
        "check if any permutation of a string is a palindrome",
    ]),
    ("math_and_bit_manipulation", 20, [
        "check if a number is prime",
        "find all prime numbers up to n using Sieve of Eratosthenes",
        "compute the greatest common divisor of two numbers",
        "compute the least common multiple of two numbers",
        "check if a number is a power of two using bit manipulation",
        "count the number of set bits in an integer",
        "reverse the bits of a 32-bit unsigned integer",
        "find the single number in an array where every other appears twice",
        "find two non-repeating numbers in array where others appear twice",
        "compute x raised to power n (implement pow)",
        "find the square root of a number without using sqrt (integer part)",
        "convert a decimal number to binary string",
        "add two binary strings and return the sum as binary string",
        "check if a number is a palindrome without converting to string",
        "find the nth ugly number (factors only 2, 3, 5)",
        "compute the factorial of n with handling for large numbers",
        "generate Pascal's triangle up to n rows",
        "find the number of trailing zeros in n factorial",
        "implement modular exponentiation",
        "find the XOR of all numbers from 1 to n efficiently",
    ]),
    ("stack_queue_heap", 20, [
        "implement a stack using two queues",
        "implement a queue using two stacks",
        "evaluate a postfix (reverse Polish notation) expression",
        "find the next greater element for each element in array",
        "implement a min-stack that supports push pop and getMin in O(1)",
        "simplify a Unix-style file path",
        "find the largest rectangle in a histogram",
        "implement a circular queue",
        "sort a stack using only another stack",
        "find the kth largest element using a min-heap",
        "merge k sorted lists using a heap",
        "find the median from a data stream using two heaps",
        "implement a priority queue from scratch",
        "check if a sequence is a valid stack pop sequence",
        "design a max frequency stack",
        "find the sliding window maximum for window size k",
        "implement an iterator that flattens a nested list",
        "evaluate an infix arithmetic expression with + - * / and parentheses",
        "design a stack that supports increment operation on bottom k elements",
        "implement a double-ended queue (deque) from scratch",
    ]),
    ("advanced_algorithms", 15, [
        "implement Trie insert search and startsWith",
        "find the longest word in dictionary that can be built character by character",
        "implement a Bloom filter with add and possibly_contains",
        "solve N-Queens problem and return all solutions",
        "find the maximum flow in a network using Ford-Fulkerson",
        "implement reservoir sampling for k items from a stream",
        "find the convex hull of a set of 2D points",
        "implement A* search algorithm on a 2D grid",
        "solve the traveling salesman problem for small n using bitmask DP",
        "implement a segment tree with range sum query and point update",
        "find the longest palindrome by concatenating two-letter words",
        "implement Rabin-Karp string matching algorithm",
        "find the maximum XOR of two numbers in an array using Trie",
        "implement a skip list with insert search and delete",
        "solve the job scheduling problem to maximize profit",
    ]),
]

SYSTEM_PROMPT = """You are an expert Python programming task designer for a benchmark.
Given a task description, you must produce a JSON object with:
1. "task_id": a unique snake_case identifier
2. "description": a clear, unambiguous task description (2-4 sentences)
3. "function_signature": the exact Python function signature (def function_name(params) -> return_type)
4. "difficulty": one of "easy", "medium", "hard"
5. "canonical_solution": a correct, clean Python implementation
6. "hidden_tests": a string containing 8-12 assert statements that thoroughly test the function, including edge cases

IMPORTANT:
- The function must be self-contained (no imports needed, or include them in the solution)
- Tests must use assert statements with the exact function name from the signature
- Include edge cases: empty inputs, single elements, large values, negative numbers where applicable
- The canonical solution MUST pass all hidden tests
- Output valid JSON only, no markdown formatting"""

def generate_task(category: str, task_hint: str, idx: int) -> dict:
    prompt = f"""Category: {category}
Task hint: {task_hint}
Task index: {idx}

Generate a complete benchmark task based on this hint. Make the task description precise and unambiguous.
Ensure the hidden tests are comprehensive and cover edge cases."""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
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
    all_tasks = []
    task_idx = 0
    
    for category, count, hints in CATEGORIES:
        print(f"\n=== Generating {count} tasks for category: {category} ===")
        for i, hint in enumerate(hints[:count]):
            task_idx += 1
            print(f"  [{task_idx}/200] {hint[:60]}...")
            task = generate_task(category, hint, task_idx)
            if task:
                all_tasks.append(task)
            
    output_path = "/home/ubuntu/e2_bench/eval_set/code_generation/tasks.json"
    with open(output_path, "w") as f:
        json.dump(all_tasks, f, indent=2)
    
    print(f"\nGenerated {len(all_tasks)} code generation tasks -> {output_path}")

if __name__ == "__main__":
    main()
