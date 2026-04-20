"""
E²-Bench: Generate Data Analysis eval tasks.
Each task has: task_id, dataset_schema, description, ground_truth_answer, difficulty, verification_hint
We generate synthetic but realistic datasets and questions with known answers.
"""
import json
import os
from openai import OpenAI

client = OpenAI()

CATEGORIES = [
    ("aggregation_and_grouping", 30, [
        "Find the total revenue per product category from a sales table",
        "Calculate the average salary by department and gender",
        "Find the top 5 customers by total purchase amount",
        "Count the number of orders per month in 2023",
        "Find the department with the highest average performance score",
        "Calculate the median house price by neighborhood",
        "Find the product with the highest return rate",
        "Calculate the total hours worked per employee per week",
        "Find the city with the most restaurants in the dataset",
        "Calculate the average rating per genre for a movie dataset",
        "Find the quarter with the highest growth rate in revenue",
        "Calculate the percentage of total sales each region contributes",
        "Find the top 3 most common complaint categories",
        "Calculate the weighted average grade per student across courses",
        "Find the supplier with the shortest average delivery time",
        "Calculate the year-over-year change in customer count",
        "Find the age group with the highest average transaction value",
        "Calculate the ratio of male to female employees per department",
        "Find the month with the highest customer churn rate",
        "Calculate the cumulative sum of donations over time",
        "Find the product pair most frequently bought together",
        "Calculate the standard deviation of test scores per class",
        "Find the day of week with the most website traffic",
        "Calculate the moving average of stock prices over 7 days",
        "Find the employee with the longest tenure in each department",
        "Calculate the conversion rate from leads to customers per channel",
        "Find the country with the highest GDP per capita from economic data",
        "Calculate the average time between repeat purchases per customer",
        "Find the top 10 most expensive items never sold",
        "Calculate the Gini coefficient of income distribution from salary data",
    ]),
    ("filtering_and_conditional", 25, [
        "Find all employees who earn above the company median salary",
        "Count students who passed all subjects with score above 60",
        "Find orders placed on weekends that exceeded 500 dollars",
        "Identify customers who made purchases in every quarter of 2023",
        "Find products with price above average but rating below 3.0",
        "Count the number of flights delayed by more than 2 hours",
        "Find patients diagnosed with condition X who are under 40",
        "Identify transactions flagged as potential fraud above 10000",
        "Find employees who received a promotion but no salary increase",
        "Count the number of days where temperature exceeded 35 degrees",
        "Find students who improved their score by more than 20 percent",
        "Identify suppliers with more than 3 late deliveries in a month",
        "Find all books published before 2000 with more than 1000 ratings",
        "Count users who logged in every day for 30 consecutive days",
        "Find restaurants with rating above 4.5 and price below 20 dollars",
        "Identify stocks that dropped more than 10 percent in a single day",
        "Find employees hired in 2020 who are still active",
        "Count products that were out of stock for more than 7 days",
        "Find customers whose total spend is in the top 1 percent",
        "Identify courses with enrollment above capacity",
        "Find all transactions where the discount exceeded 50 percent",
        "Count the number of projects completed ahead of schedule",
        "Find patients with BMI above 30 and blood pressure above 140",
        "Identify emails sent outside business hours that got replies",
        "Find the number of unique users who visited more than 10 pages",
    ]),
    ("joins_and_relationships", 25, [
        "Find customers who placed orders but never left a review",
        "Calculate the total revenue per salesperson by joining sales and employee tables",
        "Find products that appear in orders but not in the current inventory",
        "Identify students enrolled in more than 3 courses simultaneously",
        "Find the manager with the most direct reports",
        "Calculate the average delivery time by joining orders and shipments",
        "Find authors who published in more than 2 different journals",
        "Identify patients who visited multiple doctors for the same condition",
        "Find the department with the highest budget utilization rate",
        "Calculate the correlation between advertising spend and sales by region",
        "Find employees whose salary is higher than their manager's",
        "Identify products sold in all stores",
        "Find customers who bought from every product category",
        "Calculate the fill rate by joining orders and inventory tables",
        "Find pairs of students who took all the same courses",
        "Identify suppliers who provide products in more than 5 categories",
        "Find the movie with the most actors from the top 100 actors list",
        "Calculate the on-time delivery rate per carrier",
        "Find teachers who teach courses in multiple departments",
        "Identify the most common diagnosis per age group by joining patient and diagnosis tables",
        "Find orders where the shipping address differs from billing address",
        "Calculate the average number of items per order by customer segment",
        "Find the project with the most cross-departmental team members",
        "Identify products that have been reviewed but never returned",
        "Find the city pair with the most flights between them",
    ]),
    ("time_series_and_trends", 25, [
        "Find the month with the highest month-over-month growth in sales",
        "Calculate the 30-day rolling average of daily active users",
        "Identify the longest streak of consecutive days with positive returns",
        "Find the seasonal pattern in monthly electricity consumption",
        "Calculate the compound annual growth rate of revenue over 5 years",
        "Find the week with the highest variance in daily temperatures",
        "Identify the trend direction (up/down/flat) for each product's sales",
        "Calculate the time lag between order placement and delivery by quarter",
        "Find the hour of day with the highest average transaction volume",
        "Identify anomalous months where sales deviated more than 2 std from mean",
        "Calculate the customer lifetime value based on purchase history",
        "Find the fastest growing product category over the last 12 months",
        "Identify the day of year with the highest average rainfall",
        "Calculate the retention rate at 30, 60, and 90 days after signup",
        "Find the period with the longest continuous decline in stock price",
        "Calculate the average session duration trend over 6 months",
        "Identify the quarter with the highest employee turnover rate",
        "Find the correlation between weather and daily sales",
        "Calculate the year-over-year percentage change in website traffic",
        "Identify the first month where cumulative profit exceeded 1 million",
        "Find the average time to resolution for support tickets by month",
        "Calculate the seasonally adjusted unemployment rate",
        "Identify the peak and trough of a cyclical sales pattern",
        "Find the date when a metric first crossed a specific threshold",
        "Calculate the exponential moving average of daily revenue",
    ]),
    ("statistical_analysis", 25, [
        "Calculate the Pearson correlation between study hours and exam scores",
        "Find the outliers in a salary dataset using the IQR method",
        "Calculate the chi-squared statistic for independence between gender and preference",
        "Find the percentile rank of each student in a class",
        "Calculate the coefficient of variation for sales across regions",
        "Determine if the mean test score differs significantly between two groups (t-test p-value)",
        "Find the skewness and kurtosis of a revenue distribution",
        "Calculate the R-squared value for a linear regression of price vs area",
        "Find the mode and frequency of the most common purchase amount",
        "Calculate the z-score for each data point in a temperature dataset",
        "Determine the probability of a value exceeding a threshold assuming normal distribution",
        "Find the interquartile range of delivery times",
        "Calculate the Spearman rank correlation between two ranked lists",
        "Find the confidence interval for the mean of a sample at 95 percent",
        "Calculate the entropy of a categorical variable distribution",
        "Determine the optimal number of bins for a histogram using Sturges rule",
        "Find the covariance matrix for a set of numerical features",
        "Calculate the RMSE between predicted and actual values",
        "Find the proportion of variance explained by the first principal component",
        "Calculate the Jaccard similarity between two sets of purchased items",
        "Determine the break-even point from cost and revenue data",
        "Find the geometric mean of annual returns",
        "Calculate the Herfindahl index for market concentration",
        "Find the point biserial correlation between a binary and continuous variable",
        "Calculate the mean absolute deviation of monthly expenses",
    ]),
    ("data_cleaning_and_edge_cases", 20, [
        "Count the number of rows with missing values in any column",
        "Find the percentage of duplicate records in a customer table",
        "Calculate the mean salary after removing the top and bottom 5 percent outliers",
        "Find columns where more than 30 percent of values are null",
        "Identify records where the end date is before the start date",
        "Count the number of inconsistent entries where age and birth year don't match",
        "Find the most common value used to fill missing entries in a column",
        "Calculate the total after correcting negative quantity values to zero",
        "Identify rows where email format is invalid",
        "Find the number of records with values outside a valid range",
        "Calculate the percentage of records that are exact duplicates",
        "Find entries where the same ID appears with conflicting information",
        "Count the number of leading or trailing whitespace issues in name fields",
        "Calculate the revenue after removing test and cancelled orders",
        "Find the number of date parsing errors in a timestamp column",
        "Identify numeric columns stored as strings and count affected rows",
        "Calculate the mean after imputing missing values with the column median",
        "Find records where the foreign key has no matching primary key",
        "Count the number of rows where categorical values are misspelled variants",
        "Calculate the impact of removing null rows vs imputing on the mean",
    ]),
]

SYSTEM_PROMPT = """You are an expert data analyst designing benchmark tasks for evaluating AI agents.
Given a task description, you must produce a JSON object with:
1. "task_id": a unique snake_case identifier
2. "description": a clear, precise task description (2-4 sentences) that specifies exactly what to compute
3. "dataset_schema": a description of the dataset columns, types, and sample values (as a string)
4. "dataset_csv_snippet": a small CSV snippet (header + 5-8 representative rows) that illustrates the data format
5. "dataset_generation_code": Python code using pandas/numpy to generate a full synthetic dataset (100-500 rows) with a known seed
6. "ground_truth_answer": the exact correct answer (number, string, or short JSON) that would result from running the correct analysis on the generated dataset
7. "ground_truth_code": Python code that computes the answer from the generated dataset
8. "difficulty": one of "easy", "medium", "hard"
9. "common_pitfalls": a list of 2-3 common mistakes an analyst might make on this task

IMPORTANT:
- The dataset_generation_code MUST use numpy.random.seed(42) for reproducibility
- The ground_truth_code MUST produce the exact ground_truth_answer when run on the generated dataset
- The ground_truth_answer should be a specific value (e.g., "42.5", "Marketing", "{'Q1': 150, 'Q2': 200}")
- Output valid JSON only, no markdown formatting"""

def generate_task(category: str, task_hint: str, idx: int) -> dict:
    prompt = f"""Category: {category}
Task hint: {task_hint}
Task index: {idx}

Generate a complete data analysis benchmark task. Make sure the dataset is realistic and the question has a single unambiguous correct answer."""

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
            print(f"  [{task_idx}/150] {hint[:60]}...")
            task = generate_task(category, hint, task_idx)
            if task:
                all_tasks.append(task)
    
    output_path = "/home/ubuntu/e2_bench/eval_set/data_analysis/tasks.json"
    with open(output_path, "w") as f:
        json.dump(all_tasks, f, indent=2)
    
    print(f"\nGenerated {len(all_tasks)} data analysis tasks -> {output_path}")

if __name__ == "__main__":
    main()
