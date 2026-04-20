#!/usr/bin/env python3
"""
E²-Bench Consistency Validation Task Generator
Generates multi-part artifacts with planted cross-context contradictions.
"""

import json
import os

TASKS = []
task_id = [0]

def add_task(category, description, artifact_parts, planted_contradictions):
    task_id[0] += 1
    TASKS.append({
        "id": f"consistency_{task_id[0]:04d}",
        "category": category,
        "description": description,
        "artifact_parts": artifact_parts,
        "planted_contradictions": planted_contradictions,
        "num_contradictions": len(planted_contradictions),
        "ground_truth": planted_contradictions
    })


# ============================================================
# Category 1: Report Text vs Data Table Contradictions
# ============================================================

report_scenarios = [
    {
        "desc": "Q4 2025 Sales Report with summary and data table",
        "parts": {
            "executive_summary": "Our Q4 2025 performance was exceptional. Total revenue reached $4.2 million, representing a 15% increase over Q3. The North America region led with $2.1 million in sales, followed by Europe at $1.3 million and Asia-Pacific at $0.8 million. Customer acquisition cost decreased to $42 per customer, and our customer retention rate improved to 94%.",
            "data_table": "| Metric | Q3 2025 | Q4 2025 | Change |\n|--------|---------|---------|--------|\n| Total Revenue | $3.65M | $4.2M | +15.1% |\n| North America | $1.8M | $2.1M | +16.7% |\n| Europe | $1.1M | $1.5M | +36.4% |\n| Asia-Pacific | $0.75M | $0.6M | -20.0% |\n| CAC | $48 | $42 | -12.5% |\n| Retention Rate | 91% | 92% | +1pp |"
        },
        "contradictions": [
            "Executive summary says Europe revenue is $1.3M but data table shows $1.5M",
            "Executive summary says Asia-Pacific revenue is $0.8M but data table shows $0.6M",
            "Executive summary says retention rate is 94% but data table shows 92%"
        ]
    },
    {
        "desc": "Annual Employee Survey Results report",
        "parts": {
            "summary": "The 2025 Employee Satisfaction Survey received responses from 847 out of 1,200 employees (71% response rate). Overall satisfaction scored 4.2 out of 5.0, up from 3.8 last year. The top-rated category was Work-Life Balance at 4.5, while Compensation & Benefits scored lowest at 3.6. Notably, the Engineering department reported the highest satisfaction at 4.4, and the Sales department reported the lowest at 3.5.",
            "detailed_results": "| Category | 2024 Score | 2025 Score | Change |\n|----------|-----------|-----------|--------|\n| Overall Satisfaction | 3.8 | 4.2 | +0.4 |\n| Work-Life Balance | 4.3 | 4.5 | +0.2 |\n| Compensation & Benefits | 3.4 | 3.9 | +0.5 |\n| Career Growth | 3.6 | 3.8 | +0.2 |\n| Management | 4.0 | 4.1 | +0.1 |\n\n| Department | 2025 Score |\n|-----------|------------|\n| Engineering | 4.4 |\n| Marketing | 4.1 |\n| Sales | 3.9 |\n| Operations | 3.7 |\n\nResponse rate: 847 / 1,200 (70.6%)"
        },
        "contradictions": [
            "Summary says Compensation & Benefits scored lowest at 3.6, but data table shows it scored 3.9",
            "Summary says Sales department reported lowest at 3.5, but data table shows Sales scored 3.9 (Operations at 3.7 is actually lowest)"
        ]
    },
    {
        "desc": "Monthly Website Analytics Report",
        "parts": {
            "highlights": "March 2026 was our best month yet for web traffic. We recorded 2.4 million unique visitors, a 22% increase from February. The bounce rate decreased to 38%, and average session duration increased to 4 minutes 12 seconds. Our top traffic source was organic search at 45%, followed by social media at 28% and direct traffic at 18%. The blog section drove 35% of all page views.",
            "analytics_data": "| Metric | Feb 2026 | Mar 2026 | Change |\n|--------|----------|----------|--------|\n| Unique Visitors | 1.97M | 2.4M | +21.8% |\n| Bounce Rate | 42% | 38% | -4pp |\n| Avg Session Duration | 3:45 | 4:12 | +0:27 |\n| Pages per Session | 3.2 | 3.8 | +18.8% |\n\n| Traffic Source | Share |\n|---------------|-------|\n| Organic Search | 45% |\n| Social Media | 22% |\n| Direct | 18% |\n| Referral | 10% |\n| Email | 5% |\n\nNote: Blog section accounted for 28% of total page views."
        },
        "contradictions": [
            "Highlights say social media traffic share is 28%, but analytics data shows 22%",
            "Highlights say blog drove 35% of page views, but analytics note says blog accounted for 28%"
        ]
    },
]

for s in report_scenarios:
    add_task("report_vs_data", s["desc"], s["parts"], s["contradictions"])


# ============================================================
# Category 2: README vs Code Contradictions
# ============================================================

readme_code_scenarios = [
    {
        "desc": "Python data processing library README vs actual code",
        "parts": {
            "readme": """# DataFlow v2.3.1

A high-performance data processing library for Python 3.8+.

## Installation
```bash
pip install dataflow
```

## Quick Start
```python
from dataflow import Pipeline, CSVLoader, JSONExporter

# Create a pipeline
pipeline = Pipeline()
pipeline.add_stage(CSVLoader("data.csv", delimiter=","))
pipeline.add_stage(JSONExporter("output.json"))
pipeline.run()
```

## Features
- Supports CSV, JSON, Parquet, and Excel formats
- Parallel processing with up to 8 worker threads
- Built-in data validation with schema enforcement
- Memory-efficient streaming for files up to 10GB

## API Reference
- `Pipeline.run(verbose=False)` - Execute the pipeline
- `Pipeline.add_stage(stage)` - Add a processing stage
- `Pipeline.validate()` - Validate pipeline configuration
- `CSVLoader(path, delimiter=",", encoding="utf-8")` - Load CSV files
- `JSONExporter(path, indent=2, ensure_ascii=True)` - Export to JSON""",
            "code": """class Pipeline:
    def __init__(self, max_workers=4):
        self.stages = []
        self.max_workers = max_workers  # Default 4, not 8
    
    def add_stage(self, stage):
        self.stages.append(stage)
    
    def execute(self, verbose=False):  # Method is 'execute', not 'run'
        for stage in self.stages:
            stage.process()
    
    # No validate() method exists

class CSVLoader:
    def __init__(self, path, separator=",", encoding="utf-8"):  # param is 'separator', not 'delimiter'
        self.path = path
        self.separator = separator
        self.encoding = encoding

class JSONExporter:
    def __init__(self, path, indent=4, ensure_ascii=False):  # defaults differ from README
        self.path = path
        self.indent = indent
        self.ensure_ascii = ensure_ascii"""
        },
        "contradictions": [
            "README says Pipeline.run() but code defines Pipeline.execute() - method name mismatch",
            "README says 'up to 8 worker threads' but code defaults to max_workers=4",
            "README documents Pipeline.validate() but this method does not exist in the code",
            "README says CSVLoader parameter is 'delimiter' but code uses 'separator'",
            "README says JSONExporter defaults are indent=2, ensure_ascii=True but code has indent=4, ensure_ascii=False"
        ]
    },
    {
        "desc": "REST API documentation vs actual endpoint implementation",
        "parts": {
            "api_docs": """# User Management API v1.0

## Endpoints

### GET /api/users
Returns a list of all users. Supports pagination.
- Query params: `page` (default: 1), `limit` (default: 20, max: 100)
- Response: `{ "users": [...], "total": int, "page": int }`
- Auth: Bearer token required

### POST /api/users
Create a new user.
- Body: `{ "name": string, "email": string, "role": "admin" | "user" | "viewer" }`
- Response: `{ "id": int, "name": string, "email": string, "role": string, "created_at": string }`
- Auth: Admin only

### DELETE /api/users/:id
Delete a user by ID.
- Response: `{ "success": true, "message": "User deleted" }`
- Auth: Admin only

### Rate Limiting
All endpoints are rate-limited to 100 requests per minute per API key.""",
            "code": """from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/v2/users', methods=['GET'])  # Route is /api/v2/users, not /api/users
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)  # param is 'per_page' not 'limit', default 50 not 20
    users = User.query.paginate(page=page, per_page=min(per_page, 50))  # max is 50, not 100
    return jsonify({
        'data': [u.to_dict() for u in users.items],  # key is 'data', not 'users'
        'total': users.total,
        'page': users.page
    })

@app.route('/api/v2/users', methods=['POST'])
def create_user():
    data = request.json
    # role validation: only 'admin' and 'member' are valid
    if data.get('role') not in ('admin', 'member'):  # 'member' not 'user', no 'viewer' role
        return jsonify({'error': 'Invalid role'}), 400
    user = User(name=data['name'], email=data['email'], role=data['role'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

# DELETE endpoint is not implemented at all"""
        },
        "contradictions": [
            "API docs say endpoint is /api/users but code uses /api/v2/users",
            "API docs say pagination param is 'limit' (default 20, max 100) but code uses 'per_page' (default 50, max 50)",
            "API docs say response key is 'users' but code returns 'data'",
            "API docs say valid roles are 'admin', 'user', 'viewer' but code only accepts 'admin', 'member'",
            "API docs document DELETE /api/users/:id but this endpoint is not implemented in the code"
        ]
    },
    {
        "desc": "Configuration file vs application behavior documentation",
        "parts": {
            "config_file": """# config.yaml
server:
  host: 0.0.0.0
  port: 8080
  max_connections: 1000
  timeout: 30  # seconds

database:
  engine: postgresql
  host: db.example.com
  port: 5432
  name: myapp_production
  pool_size: 20
  ssl: true

cache:
  backend: redis
  host: cache.example.com
  port: 6379
  ttl: 3600  # 1 hour
  max_memory: 512mb

logging:
  level: INFO
  format: json
  output: /var/log/myapp/app.log
  rotation: daily""",
            "deployment_guide": """# Deployment Guide

## Server Configuration
The application runs on port **3000** by default and supports up to **500 concurrent connections**. Connection timeout is set to **60 seconds**.

## Database
We use **MySQL** as our primary database, hosted at db.example.com. The connection pool maintains **10 connections** by default. SSL is disabled for internal network communication.

## Caching
Redis is used for caching with a default TTL of **30 minutes** (1800 seconds). The cache server runs on the default Redis port **6379** with a memory limit of **1GB**.

## Logging
Application logs are written in **plain text** format to `/var/log/myapp/app.log` with **weekly** rotation. Default log level is **DEBUG**."""
        },
        "contradictions": [
            "Config says port 8080 but deployment guide says port 3000",
            "Config says max_connections 1000 but guide says 500 concurrent connections",
            "Config says timeout 30s but guide says 60 seconds",
            "Config says engine postgresql but guide says MySQL",
            "Config says pool_size 20 but guide says 10 connections",
            "Config says ssl true but guide says SSL is disabled",
            "Config says cache ttl 3600 (1 hour) but guide says 30 minutes (1800 seconds)",
            "Config says max_memory 512mb but guide says 1GB",
            "Config says logging format json but guide says plain text",
            "Config says rotation daily but guide says weekly",
            "Config says logging level INFO but guide says DEBUG"
        ]
    },
]

for s in readme_code_scenarios:
    add_task("readme_vs_code", s["desc"], s["parts"], s["contradictions"])


# ============================================================
# Category 3: Chart Description vs Chart Data Contradictions
# ============================================================

chart_scenarios = [
    {
        "desc": "Marketing report with chart description contradicting the data",
        "parts": {
            "chart_description": "Figure 3 shows the monthly active users (MAU) trend for 2025. As illustrated, MAU grew steadily throughout the year, starting at 120K in January and reaching a peak of 285K in December. The most significant growth occurred in Q3, with a 40% quarter-over-quarter increase. There were no months with declining MAU.",
            "chart_data": "| Month | MAU (thousands) |\n|-------|----------------|\n| Jan | 120 |\n| Feb | 128 |\n| Mar | 135 |\n| Apr | 142 |\n| May | 155 |\n| Jun | 168 |\n| Jul | 195 |\n| Aug | 210 |\n| Sep | 198 |\n| Oct | 225 |\n| Nov | 248 |\n| Dec | 265 |"
        },
        "contradictions": [
            "Description says peak of 285K in December but data shows 265K",
            "Description says 'no months with declining MAU' but September (198K) declined from August (210K)",
            "Description says Q3 had 40% QoQ increase: Q2 end=168K, Q3 end=198K, actual increase is only 17.9%"
        ]
    },
    {
        "desc": "Budget allocation report with pie chart description vs data",
        "parts": {
            "narrative": "The 2026 budget allocates resources across five departments. Engineering receives the largest share at 35%, followed by Marketing at 25%, Sales at 20%, Operations at 12%, and HR at 8%. The total budget is $5 million. Compared to 2025, Engineering's share increased by 5 percentage points while Marketing's decreased by 3 percentage points.",
            "budget_data": "| Department | 2025 Budget | 2025 % | 2026 Budget | 2026 % |\n|-----------|-------------|--------|-------------|--------|\n| Engineering | $1,400,000 | 28% | $1,750,000 | 35% |\n| Marketing | $1,250,000 | 25% | $1,100,000 | 22% |\n| Sales | $1,100,000 | 22% | $1,000,000 | 20% |\n| Operations | $750,000 | 15% | $650,000 | 13% |\n| HR | $500,000 | 10% | $500,000 | 10% |\n| **Total** | **$5,000,000** | **100%** | **$5,000,000** | **100%** |"
        },
        "contradictions": [
            "Narrative says Marketing is 25% but data shows 22%",
            "Narrative says Operations is 12% but data shows 13%",
            "Narrative says HR is 8% but data shows 10%",
            "Narrative says Engineering increased by 5pp (from 30% to 35%) but data shows increase from 28% to 35% = 7pp",
            "Narrative says Marketing decreased by 3pp but data shows decrease from 25% to 22% = 3pp (this one is actually correct)"
        ]
    },
    {
        "desc": "Customer satisfaction survey with summary contradicting raw data",
        "parts": {
            "summary_paragraph": "Our NPS survey collected 1,500 responses. The overall NPS score is +45, calculated from 62% Promoters, 21% Passives, and 17% Detractors. The Enterprise segment had the highest NPS at +58, while the SMB segment scored +32. Response rate was 75% (1,500 out of 2,000 customers surveyed).",
            "raw_data": "| Segment | Responses | Promoters | Passives | Detractors | NPS |\n|---------|-----------|-----------|----------|------------|-----|\n| Enterprise | 400 | 68% | 18% | 14% | +54 |\n| Mid-Market | 500 | 60% | 22% | 18% | +42 |\n| SMB | 600 | 58% | 24% | 18% | +40 |\n| **Total** | **1,500** | **61%** | **22%** | **17%** | **+44** |"
        },
        "contradictions": [
            "Summary says overall NPS is +45 but data shows +44",
            "Summary says 62% Promoters but data shows 61%",
            "Summary says 21% Passives but data shows 22%",
            "Summary says Enterprise NPS is +58 but data shows +54",
            "Summary says SMB NPS is +32 but data shows +40"
        ]
    },
]

for s in chart_scenarios:
    add_task("chart_vs_data", s["desc"], s["parts"], s["contradictions"])


# ============================================================
# Category 4: Slide Deck Internal Contradictions
# ============================================================

slide_scenarios = [
    {
        "desc": "Startup pitch deck with contradictions across slides",
        "parts": {
            "slide_1_title": "TechFlow - Series A Pitch Deck",
            "slide_3_problem": "The global market for workflow automation is valued at $12.5 billion in 2025 and is projected to reach $28 billion by 2030, growing at a CAGR of 17.5%. Currently, 78% of enterprises still rely on manual processes for critical workflows.",
            "slide_5_solution": "TechFlow's AI-powered platform automates complex workflows with zero code. Our platform currently serves 340 enterprise customers across 12 countries.",
            "slide_7_traction": "Key Metrics:\n- 280 enterprise customers (up from 150 last year)\n- $4.2M ARR (growing 120% YoY)\n- 15 countries with active users\n- 99.9% uptime SLA",
            "slide_9_financials": "Revenue Projections:\n- 2025: $4.2M ARR\n- 2026: $8.5M ARR (102% growth)\n- 2027: $18M ARR\n- 2028: $35M ARR\n\nCurrent burn rate: $350K/month\nRunway: 18 months (with $6.3M in bank)",
            "slide_10_ask": "We are raising $10 million Series A at a $50 million pre-money valuation. Funds will be used for: Engineering (45%), Sales (30%), Marketing (15%), Operations (10%). With this funding, we project reaching $20M ARR by end of 2027."
        },
        "contradictions": [
            "Slide 5 says 340 enterprise customers but Slide 7 says 280 enterprise customers",
            "Slide 5 says 12 countries but Slide 7 says 15 countries",
            "Slide 7 says 120% YoY growth but Slide 9 projects 2025-2026 growth at only 102%",
            "Slide 9 says $18M ARR by 2027 but Slide 10 says $20M ARR by end of 2027"
        ]
    },
    {
        "desc": "Product roadmap presentation with timeline contradictions",
        "parts": {
            "slide_2_overview": "Our 2026 product roadmap focuses on three major releases: v3.0 in Q1 (AI Assistant), v3.5 in Q2 (Enterprise SSO & RBAC), and v4.0 in Q4 (Multi-cloud deployment). Each release has been carefully planned with dedicated engineering sprints.",
            "slide_4_q1_details": "v3.0 - AI Assistant (Release: March 2026)\n- Natural language query interface\n- Automated report generation\n- Smart suggestions engine\n- Team: 8 engineers, 2 designers\n- Status: Development started, 60% complete",
            "slide_6_q2_details": "v3.5 - Enterprise Features (Release: July 2026)\n- SSO integration (SAML, OIDC)\n- Role-based access control\n- Audit logging\n- SOC 2 compliance\n- Team: 6 engineers, 1 security specialist\n- Status: Planning phase",
            "slide_8_q4_details": "v4.0 - Multi-cloud (Release: November 2026)\n- AWS, GCP, Azure support\n- Kubernetes orchestration\n- Zero-downtime migration\n- Team: 12 engineers, 3 DevOps\n- Status: Research phase\n- Dependencies: Requires v3.0 and v3.5 to be complete",
            "slide_10_resources": "Total engineering team: 22 engineers\nQ1 allocation: v3.0 (8 engineers), v3.5 prep (4 engineers), maintenance (10 engineers)\nQ2 allocation: v3.5 (6 engineers), v4.0 prep (6 engineers), maintenance (10 engineers)"
        },
        "contradictions": [
            "Overview says v3.5 releases in Q2 but detail slide says July 2026 which is Q3",
            "Overview says v4.0 releases in Q4 but detail slide says November which is technically Q4 (consistent, but v3.5 in July means only 4 months gap)",
            "Resource slide shows 22 total engineers but Q1 allocation adds up to 22 (8+4+10) while Q2 adds up to 22 (6+6+10) - but v3.0 team of 8 engineers is not accounted for in Q2",
            "v3.0 detail says 60% complete but v3.5 is still in planning and v4.0 in research, yet the resource slide already allocates engineers to v4.0 prep in Q2"
        ]
    },
]

for s in slide_scenarios:
    add_task("slide_deck", s["desc"], s["parts"], s["contradictions"])


# ============================================================
# Category 5: Multi-file Project Contradictions
# ============================================================

project_scenarios = [
    {
        "desc": "Python package with contradictions between pyproject.toml, README, and code",
        "parts": {
            "pyproject_toml": """[project]
name = "fastcache"
version = "1.2.0"
description = "A high-performance caching library"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [{name = "Jane Developer", email = "jane@example.com"}]
dependencies = [
    "redis>=4.0",
    "msgpack>=1.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "black", "mypy"]""",
            "readme": """# FastCache v1.3.0

A blazing-fast caching library for Python 3.8+.

## Installation
```
pip install fastcache
```

## Requirements
- Python 3.8 or higher
- Redis 5.0+ (optional, for distributed caching)
- No additional dependencies required

## License
Apache 2.0

## Author
John Smith (john@example.com)""",
            "init_py": """\"\"\"FastCache - High-performance caching library.\"\"\"

__version__ = "1.1.5"
__author__ = "Jane Developer"

import sys
if sys.version_info < (3, 9):
    raise RuntimeError("FastCache requires Python 3.9+")
"""
        },
        "contradictions": [
            "Three different version numbers: pyproject.toml says 1.2.0, README says 1.3.0, __init__.py says 1.1.5",
            "Three different Python version requirements: pyproject.toml says >=3.10, README says 3.8+, code checks for 3.9+",
            "README says 'No additional dependencies required' but pyproject.toml lists redis and msgpack as dependencies",
            "pyproject.toml says MIT license but README says Apache 2.0",
            "pyproject.toml says author is Jane Developer but README says John Smith"
        ]
    },
    {
        "desc": "Web app with contradictions between frontend, backend, and docs",
        "parts": {
            "frontend_config": """// frontend/src/config.ts
export const API_CONFIG = {
  BASE_URL: 'https://api.myapp.com/v2',
  TIMEOUT: 5000,  // 5 seconds
  MAX_RETRIES: 3,
  AUTH_HEADER: 'X-Auth-Token',
  PAGINATION_LIMIT: 25,
};

export const FEATURES = {
  DARK_MODE: true,
  NOTIFICATIONS: true,
  FILE_UPLOAD_MAX_SIZE: 10 * 1024 * 1024,  // 10MB
  SUPPORTED_FILE_TYPES: ['.pdf', '.doc', '.docx', '.xlsx'],
};""",
            "backend_config": """# backend/config.py
class Config:
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'
    
    REQUEST_TIMEOUT = 30  # seconds
    MAX_RETRIES = 5
    AUTH_HEADER_NAME = 'Authorization'
    
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 200
    
    MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xlsx', '.png', '.jpg'}""",
            "api_documentation": """# API Documentation

## Base URL
`https://api.myapp.com/v1`

## Authentication
All requests must include the `Authorization` header with a Bearer token.

## Pagination
Default page size: 25 items. Maximum: 100 items.

## File Upload
Maximum file size: 20MB
Supported formats: PDF, DOC, DOCX, XLSX, PNG, JPG, GIF"""
        },
        "contradictions": [
            "Frontend uses API v2 but backend defines v1 and docs say v1",
            "Frontend timeout is 5s but backend timeout is 30s",
            "Frontend max retries is 3 but backend is 5",
            "Frontend auth header is 'X-Auth-Token' but backend uses 'Authorization'",
            "Frontend pagination limit is 25 but backend default is 50",
            "Frontend max upload is 10MB, backend is 5MB, docs say 20MB - three different values",
            "Frontend supports 4 file types, backend supports 6, docs list 7 (adds GIF)",
            "Docs say max pagination is 100 but backend allows up to 200"
        ]
    },
]

for s in project_scenarios:
    add_task("multi_file_project", s["desc"], s["parts"], s["contradictions"])


# ============================================================
# Category 6: Email/Communication Contradictions
# ============================================================

email_scenarios = [
    {
        "desc": "Meeting invitation with contradictory details",
        "parts": {
            "email_subject": "Quarterly Business Review - Tuesday, April 15th at 2:00 PM EST",
            "email_body": "Hi Team,\n\nPlease join us for the Q1 2026 Quarterly Business Review.\n\nDate: Wednesday, April 15, 2026\nTime: 3:00 PM PST\nLocation: Conference Room B, 3rd Floor\nDuration: 90 minutes\n\nAgenda:\n1. Q1 Financial Review (20 min)\n2. Product Update (20 min)\n3. Customer Success Metrics (15 min)\n4. Q2 Planning (25 min)\n\nPlease review the attached Q1 report before the meeting.\n\nBest,\nSarah",
            "calendar_invite": "Event: Q1 2026 Business Review\nDate: April 15, 2026 (Tuesday)\nTime: 2:00 PM - 3:00 PM EST\nLocation: Conference Room A, 2nd Floor\nOrganizer: Sarah Johnson\nRequired: All department heads"
        },
        "contradictions": [
            "Subject says Tuesday but email body says Wednesday (April 15, 2026 is actually a Wednesday)",
            "Subject says 2:00 PM EST but email body says 3:00 PM PST (these are actually the same time, but calendar says 2:00-3:00 PM EST which is only 1 hour)",
            "Email says duration is 90 minutes but calendar shows 1 hour (2:00-3:00 PM)",
            "Email says Conference Room B, 3rd Floor but calendar says Conference Room A, 2nd Floor",
            "Agenda items add up to 80 minutes but meeting is stated as 90 minutes"
        ]
    },
    {
        "desc": "Job posting with contradictory requirements",
        "parts": {
            "job_title_section": "Senior Software Engineer (5-8 years experience)\nRemote-First | Full-Time | $150K-$180K",
            "job_description": "We are looking for a mid-level software engineer to join our growing team. The ideal candidate has 3+ years of experience with Python and JavaScript. This is an in-office position based in our San Francisco headquarters. Compensation range: $120K-$160K plus equity.",
            "requirements_section": "Requirements:\n- 7+ years of professional software development experience\n- Expert in Python, Go, and Rust\n- Bachelor's degree required, Master's preferred\n- Must be willing to relocate to New York City\n- Experience with distributed systems at scale"
        },
        "contradictions": [
            "Title says 'Senior' but description says 'mid-level'",
            "Title says 5-8 years but description says 3+ years and requirements say 7+ years",
            "Title says Remote-First but description says in-office and requirements say relocate",
            "Title says $150K-$180K but description says $120K-$160K",
            "Description mentions Python and JavaScript but requirements list Python, Go, and Rust",
            "Description says San Francisco but requirements say New York City"
        ]
    },
]

for s in email_scenarios:
    add_task("communication", s["desc"], s["parts"], s["contradictions"])


# ============================================================
# Category 7: Tutorial/Documentation Step Contradictions
# ============================================================

tutorial_scenarios = [
    {
        "desc": "Installation tutorial with contradictory steps",
        "parts": {
            "prerequisites": "Before you begin, ensure you have:\n- Node.js v18 or higher\n- npm v9 or higher\n- Git installed\n- A GitHub account",
            "step_1": "Step 1: Clone the repository\n```bash\ngit clone https://github.com/example/myproject.git\ncd myproject\n```",
            "step_2": "Step 2: Install dependencies\n```bash\nyarn install\n```\nThis will install all required packages listed in package.json.",
            "step_3": "Step 3: Configure environment\n```bash\ncp .env.example .env\n```\nEdit .env and set your DATABASE_URL to your PostgreSQL connection string.",
            "step_4": "Step 4: Run database migrations\n```bash\nnpm run migrate\n```\nThis will set up your MySQL database schema.",
            "step_5": "Step 5: Start the development server\n```bash\npnpm dev\n```\nThe app will be available at http://localhost:5173"
        },
        "contradictions": [
            "Prerequisites say npm but Step 2 uses yarn and Step 5 uses pnpm - three different package managers",
            "Step 3 says PostgreSQL but Step 4 says MySQL - different databases",
            "Steps use three different package managers: yarn install, npm run migrate, pnpm dev"
        ]
    },
    {
        "desc": "API integration guide with contradictory examples",
        "parts": {
            "introduction": "This guide shows how to integrate with our REST API using JSON. All requests should use the `Content-Type: application/json` header. The base URL is `https://api.service.com/v3`.",
            "auth_section": "Authentication:\nInclude your API key in the `X-API-Key` header:\n```\ncurl -H 'Authorization: Bearer YOUR_TOKEN' https://api.service.com/v2/users\n```",
            "example_request": "Example - Create a user:\n```python\nimport requests\n\nresponse = requests.post(\n    'https://api.service.com/v3/users',\n    headers={'X-API-Key': 'your-key-here'},\n    data='<user><name>John</name></user>',  # XML body\n    timeout=10\n)\n```",
            "error_handling": "Error responses use standard HTTP status codes. All errors return JSON:\n```json\n{\"error\": {\"code\": 400, \"message\": \"Invalid request\"}}\n```\nNote: Error responses are returned as XML for backwards compatibility."
        },
        "contradictions": [
            "Introduction says REST API using JSON but example sends XML body",
            "Introduction says base URL is v3 but auth example uses v2",
            "Auth section says use 'Authorization: Bearer' header but example uses 'X-API-Key' header",
            "Error handling section says errors return JSON but then says errors are returned as XML"
        ]
    },
]

for s in tutorial_scenarios:
    add_task("tutorial_docs", s["desc"], s["parts"], s["contradictions"])


# ============================================================
# Category 8: Resume/Profile Contradictions
# ============================================================

resume_scenarios = [
    {
        "desc": "Professional resume with internal contradictions",
        "parts": {
            "header": "ALEX CHEN\nSenior Data Scientist | 8 Years Experience\nSan Francisco, CA | alex@email.com | linkedin.com/in/alexchen",
            "summary": "Results-driven machine learning engineer with 6 years of experience in NLP and computer vision. Based in New York City. Passionate about building scalable ML systems that drive business impact. PhD in Computer Science from Stanford University.",
            "experience": "WORK EXPERIENCE\n\nLead Data Scientist | TechCorp | 2022 - Present (4 years)\n- Led a team of 12 data scientists\n- Increased model accuracy by 35%\n- Managed $2M annual budget\n\nSenior ML Engineer | DataCo | 2019 - 2022 (3 years)\n- Built recommendation engine serving 5M users\n- Reduced inference latency by 60%\n\nData Analyst | StartupXYZ | 2018 - 2019 (1 year)\n- Developed dashboards and reports",
            "education": "EDUCATION\n\nMS in Computer Science | MIT | 2018\nBS in Mathematics | UC Berkeley | 2016"
        },
        "contradictions": [
            "Header says 'Senior Data Scientist' but summary says 'machine learning engineer'",
            "Header says 8 years experience but work history shows only ~8 years (2018-2026) while summary says 6 years",
            "Header says San Francisco but summary says New York City",
            "Summary says PhD from Stanford but education section shows MS from MIT (no PhD listed)",
            "Experience shows work starting in 2018 but education shows MS completed in 2018 and BS in 2016 - timeline is tight but possible"
        ]
    },
]

for s in resume_scenarios:
    add_task("resume_profile", s["desc"], s["parts"], s["contradictions"])


# ============================================================
# Save all tasks
# ============================================================

os.makedirs("/home/ubuntu/e2_bench/eval_set/consistency_validation", exist_ok=True)
output_path = "/home/ubuntu/e2_bench/eval_set/consistency_validation/tasks.json"
with open(output_path, "w") as f:
    json.dump(TASKS, f, indent=2)

print(f"Generated {len(TASKS)} consistency validation tasks")

from collections import Counter
cats = Counter(t["category"] for t in TASKS)
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")
