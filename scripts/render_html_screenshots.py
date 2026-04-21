#!/usr/bin/env python3
"""
Render perceptual validation HTML pages to screenshots for visualization.
Uses headless Chromium via subprocess to capture screenshots.
"""
import json
import os
import subprocess
import tempfile

EVAL_DIR = "/home/ubuntu/e2_bench/eval_set/perceptual_validation"
OUTPUT_DIR = "/home/ubuntu/e2_bench/eval_set/perceptual_validation/screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load tasks
with open(os.path.join(EVAL_DIR, "tasks.json")) as f:
    tasks = json.load(f)

print(f"Rendering {len(tasks)} perceptual validation tasks to screenshots...")

# Render a sample (first 10 tasks) to keep it manageable
sample_tasks = tasks[:10]

for i, task in enumerate(sample_tasks):
    task_id = task.get("id", f"task_{i}")
    html_content = task.get("bugged_html", task.get("html", ""))
    
    if not html_content:
        print(f"  [{i+1}] {task_id}: No HTML content found, skipping")
        continue
    
    # Write HTML to temp file
    html_path = os.path.join(OUTPUT_DIR, f"{task_id}.html")
    with open(html_path, "w") as f:
        f.write(html_content)
    
    # Use headless Chromium to capture screenshot
    screenshot_path = os.path.join(OUTPUT_DIR, f"{task_id}.png")
    
    try:
        result = subprocess.run(
            [
                "chromium",
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                "--screenshot=" + screenshot_path,
                "--window-size=1280,900",
                "--hide-scrollbars",
                "file://" + html_path,
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        
        if os.path.exists(screenshot_path):
            size = os.path.getsize(screenshot_path)
            bugs = task.get("planted_bugs", task.get("bugs", []))
            bug_types = bugs if isinstance(bugs, list) else []
            print(f"  [{i+1}] {task_id}: OK ({size} bytes) | Bugs: {bug_types}")
        else:
            print(f"  [{i+1}] {task_id}: Screenshot not created")
            if result.stderr:
                print(f"    stderr: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        print(f"  [{i+1}] {task_id}: Timeout")
    except Exception as e:
        print(f"  [{i+1}] {task_id}: Error: {e}")

# Count results
screenshots = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".png")]
print(f"\nDone! {len(screenshots)} screenshots saved to {OUTPUT_DIR}")
