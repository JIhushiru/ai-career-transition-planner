"""Comprehensive role validation and correction script.

Fixes based on cross-referenced 2025-2026 Philippine salary data from:
- Glassdoor PH, PayScale PH, Jobstreet PH, Indeed PH
- Manila Recruitment IT Salary Guide 2025
- Michael Page PH Salary Guide 2025
- Robert Walters PH Salary Survey 2025
- NodeFlair, SalaryExpert/ERI, Second Talent

All salaries are MONTHLY in PHP for Metro Manila (NCR).
"""

import json
from pathlib import Path

ROLES_FILE = Path(__file__).parent.parent / "app" / "data" / "roles_ph.json"
PHP_TO_USD = 56  # approximate exchange rate


def format_usd(php_amount: int) -> str:
    usd = round(php_amount / PHP_TO_USD / 50) * 50  # round to nearest $50
    if usd < 100:
        usd = round(php_amount / PHP_TO_USD / 10) * 10
    return f"${usd:,}"


# ──────────────────────────────────────────────────────
# Roles to REMOVE (duplicates)
# ──────────────────────────────────────────────────────
REMOVE_TITLES = {
    # "CFO" duplicates "Chief Financial Officer"
    "CFO",
    # "CTO" in Engineering duplicates "Chief Technology Officer" in Management
    "CTO",
    # "BPO Team Leader" in Management duplicates "BPO Team Lead" in BPO/Operations
    "BPO Team Leader",
}

# We also need to remove the SECOND "Senior Financial Analyst" (the batch-2 one
# with PHP 60,000 - 120,000) and the SECOND "Database Administrator" (under Data).
# We'll handle those specially below.


# ──────────────────────────────────────────────────────
# Corrections: keyed by title (and optionally category to disambiguate)
# Only non-None fields will be overwritten.
# ──────────────────────────────────────────────────────
CORRECTIONS: list[dict] = [
    # ── Engineering Mid ────────────────────────────────
    {"title": "Software Engineer", "salary_min": 35000, "salary_max": 70000},
    {"title": "Backend Engineer", "salary_min": 40000, "salary_max": 80000},
    {"title": "Backend Developer", "salary_min": 40000, "salary_max": 75000},
    {"title": "Frontend Engineer", "salary_min": 30000, "salary_max": 70000},
    {"title": "Frontend Developer", "salary_min": 35000, "salary_max": 70000},
    {"title": "Full-Stack Engineer", "salary_min": 40000, "salary_max": 85000},
    {"title": "Full-Stack Developer", "salary_min": 40000, "salary_max": 80000},
    {"title": "DevOps Engineer", "salary_min": 50000, "salary_max": 100000},
    {"title": "QA Engineer", "salary_min": 25000, "salary_max": 55000},
    {"title": "Mobile Developer", "salary_min": 35000, "salary_max": 75000},
    {"title": "Data Engineer", "salary_min": 50000, "salary_max": 100000},
    {"title": "Machine Learning Engineer", "salary_min": 50000, "salary_max": 100000},
    {"title": "ML Engineer", "salary_min": 45000, "salary_max": 85000},
    {"title": "MLOps Engineer", "salary_min": 50000, "salary_max": 90000},
    {"title": "Platform Engineer", "salary_min": 65000, "salary_max": 120000},
    {"title": "Site Reliability Engineer", "salary_min": 55000, "salary_max": 110000},
    {"title": "AI Engineer", "salary_min": 50000, "salary_max": 100000},
    {"title": "AI Research Scientist", "salary_min": 55000, "salary_max": 100000, "seniority": "mid", "min_years_experience": 3},
    {"title": "Cybersecurity Engineer", "salary_min": 45000, "salary_max": 80000},
    {"title": "Data Architect", "salary_min": 50000, "salary_max": 90000, "seniority": "senior", "min_years_experience": 5},
    {"title": "Enterprise Architect", "salary_min": 60000, "salary_max": 110000, "seniority": "senior", "min_years_experience": 5},
    {"title": "Infrastructure Architect", "salary_min": 55000, "salary_max": 100000, "seniority": "senior", "min_years_experience": 5},
    {"title": "Solutions Architect", "salary_min": 60000, "salary_max": 110000, "seniority": "senior", "min_years_experience": 5},
    {"title": "Security Architect", "category": "Engineering", "salary_min": 55000, "salary_max": 100000, "seniority": "senior", "min_years_experience": 5},
    {"title": "Blockchain Developer", "salary_min": 40000, "salary_max": 80000},
    {"title": "Embedded Systems Engineer", "salary_min": 35000, "salary_max": 70000},
    {"title": "BI Developer", "salary_min": 35000, "salary_max": 65000},
    {"title": "QA Automation Engineer", "salary_min": 35000, "salary_max": 70000},
    {"title": "Manual QA Tester", "salary_min": 22000, "salary_max": 45000},
    {"title": "Software Developer", "salary_min": 35000, "salary_max": 65000},
    {"title": "Technical Writer", "salary_min": 25000, "salary_max": 50000},
    {"title": "Developer Advocate", "salary_min": 40000, "salary_max": 80000},
    {"title": "Automation Engineer", "salary_min": 35000, "salary_max": 70000},
    {"title": "DevSecOps Engineer", "salary_min": 50000, "salary_max": 100000},
    {"title": "Game Developer", "salary_min": 30000, "salary_max": 65000},
    {"title": "Release Engineer", "salary_min": 40000, "salary_max": 75000},
    {"title": "Cloud Solutions Architect", "salary_min": 70000, "salary_max": 130000},

    # ── Engineering Senior ─────────────────────────────
    {"title": "Senior Software Engineer", "salary_min": 80000, "salary_max": 150000},
    {"title": "Senior Backend Developer", "salary_min": 75000, "salary_max": 130000},
    {"title": "Senior Frontend Developer", "salary_min": 70000, "salary_max": 120000},
    {"title": "Senior Full-Stack Developer", "salary_min": 75000, "salary_max": 130000},
    {"title": "Senior DevOps Engineer", "salary_min": 80000, "salary_max": 140000},
    {"title": "Senior Data Engineer", "salary_min": 80000, "salary_max": 140000},
    {"title": "Senior QA Engineer", "salary_min": 50000, "salary_max": 90000},
    {"title": "Senior Mobile Developer", "salary_min": 70000, "salary_max": 120000},
    {"title": "Senior Network Engineer", "salary_min": 55000, "salary_max": 100000},
    {"title": "Senior Cybersecurity Analyst", "salary_min": 65000, "salary_max": 120000},
    {"title": "Senior Engineering Manager", "salary_min": 100000, "salary_max": 180000},
    {"title": "Senior BI Developer", "salary_min": 50000, "salary_max": 90000},
    {"title": "Senior Software Developer", "salary_min": 70000, "salary_max": 120000},

    # ── Engineering Lead/Staff ─────────────────────────
    {"title": "Staff Engineer", "salary_min": 120000, "salary_max": 200000},
    {"title": "Technical Lead", "salary_min": 100000, "salary_max": 180000},
    {"title": "Principal Engineer", "salary_min": 130000, "salary_max": 220000},
    {"title": "Software Architect", "salary_min": 100000, "salary_max": 180000},
    {"title": "Head of Data Engineering", "salary_min": 110000, "salary_max": 180000},
    {"title": "Mobile Engineering Lead", "salary_min": 90000, "salary_max": 160000},

    # ── Engineering Executive ──────────────────────────
    {"title": "Data Engineering Manager", "salary_min": 100000, "salary_max": 170000, "seniority": "senior", "min_years_experience": 7},

    # ── Data ───────────────────────────────────────────
    {"title": "Data Analyst", "salary_min": 25000, "salary_max": 50000},
    {"title": "Data Scientist", "salary_min": 45000, "salary_max": 100000},
    {"title": "BI Analyst", "salary_min": 28000, "salary_max": 55000},
    {"title": "Analytics Engineer", "salary_min": 42000, "salary_max": 85000},
    {"title": "Senior Data Scientist", "salary_min": 70000, "salary_max": 130000},
    {"title": "Senior Database Administrator", "salary_min": 50000, "salary_max": 90000},
    {"title": "Database Administrator", "category": "Data", "_remove": True},  # duplicate of IT one
    {"title": "Lead Data Scientist", "salary_min": 90000, "salary_max": 150000},
    {"title": "Head of Data Science", "salary_min": 100000, "salary_max": 170000},
    {"title": "BI Manager", "salary_min": 75000, "salary_max": 120000, "seniority": "senior", "min_years_experience": 7},
    {"title": "Senior Data Analyst", "salary_min": 45000, "salary_max": 80000},
    {"title": "Data Governance Analyst", "salary_min": 38000, "salary_max": 65000},
    {"title": "Junior Data Analyst", "salary_min": 18000, "salary_max": 32000},
    {"title": "Junior Data Scientist", "salary_min": 25000, "salary_max": 42000},

    # ── Design ─────────────────────────────────────────
    {"title": "UI/UX Designer", "salary_min": 25000, "salary_max": 50000},
    {"title": "Product Designer", "salary_min": 30000, "salary_max": 55000},
    {"title": "Graphic Designer", "salary_min": 20000, "salary_max": 38000},
    {"title": "Design Lead", "salary_min": 50000, "salary_max": 85000, "min_years_experience": 5},
    {"title": "Head of Design", "salary_min": 65000, "salary_max": 110000},
    {"title": "Junior UI/UX Designer", "salary_min": 18000, "salary_max": 30000},
    {"title": "Senior UI/UX Designer", "salary_min": 40000, "salary_max": 75000},
    {"title": "Brand Designer", "salary_min": 22000, "salary_max": 42000},
    {"title": "Content Designer", "salary_min": 25000, "salary_max": 48000},
    {"title": "Motion Designer", "salary_min": 25000, "salary_max": 50000},
    {"title": "UX Researcher", "salary_min": 28000, "salary_max": 55000},

    # ── Finance ────────────────────────────────────────
    {"title": "Bookkeeper", "salary_min": 15000, "salary_max": 25000},
    {"title": "Accounting Clerk", "salary_min": 15000, "salary_max": 25000},
    {"title": "Accounts Payable Specialist", "salary_min": 16000, "salary_max": 28000},
    {"title": "Staff Accountant", "salary_min": 18000, "salary_max": 28000},
    {"title": "Junior Accountant", "salary_min": 18000, "salary_max": 28000},
    {"title": "Internal Auditor", "salary_min": 22000, "salary_max": 38000},
    {"title": "Accountant", "salary_min": 25000, "salary_max": 40000},
    {"title": "Senior Accountant", "salary_min": 35000, "salary_max": 55000},
    {"title": "Tax Analyst", "salary_min": 25000, "salary_max": 45000},
    {"title": "Tax Accountant", "salary_min": 28000, "salary_max": 50000},
    {"title": "Tax Consultant", "salary_min": 35000, "salary_max": 60000},
    {"title": "Tax Tech Consultant", "salary_min": 35000, "salary_max": 60000},
    {"title": "Financial Analyst", "salary_min": 25000, "salary_max": 45000},
    # Keep the original Senior Financial Analyst (55k-100k), remove batch-2 duplicate (handled below)
    {"title": "Senior Financial Analyst", "category": "Finance", "salary_min": 45000, "salary_max": 75000, "_match_first": True},
    {"title": "Auditor", "salary_min": 20000, "salary_max": 38000},
    {"title": "Senior Auditor", "salary_min": 40000, "salary_max": 65000},
    {"title": "Audit Manager", "salary_min": 50000, "salary_max": 80000},
    {"title": "Investment Analyst", "salary_min": 30000, "salary_max": 55000},
    {"title": "Payroll Specialist", "salary_min": 22000, "salary_max": 38000},
    {"title": "Controller", "salary_min": 70000, "salary_max": 130000},
    {"title": "Credit Analyst", "salary_min": 25000, "salary_max": 45000},
    {"title": "Budget Analyst", "salary_min": 28000, "salary_max": 48000},
    {"title": "Risk Analyst", "salary_min": 30000, "salary_max": 55000},
    {"title": "Treasury Analyst", "salary_min": 28000, "salary_max": 50000},
    {"title": "Account Executive", "salary_min": 20000, "salary_max": 35000},
    {"title": "Account Manager", "salary_min": 40000, "salary_max": 70000, "seniority": "senior", "min_years_experience": 5},
    {"title": "Finance Manager", "salary_min": 65000, "salary_max": 110000, "seniority": "senior", "min_years_experience": 7},
    {"title": "Accounting Manager", "salary_min": 55000, "salary_max": 85000, "seniority": "senior", "min_years_experience": 7},
    {"title": "Tax Manager", "salary_min": 55000, "salary_max": 90000, "seniority": "senior", "min_years_experience": 7},
    {"title": "FP&A Manager", "salary_min": 80000, "salary_max": 140000, "seniority": "senior", "min_years_experience": 7},
    {"title": "Chief Financial Officer", "salary_min": 150000, "salary_max": 400000},
    {"title": "VP of Finance", "salary_min": 120000, "salary_max": 300000},

    # ── HR ─────────────────────────────────────────────
    {"title": "Administrative Assistant", "salary_min": 16000, "salary_max": 25000},
    {"title": "Executive Assistant", "salary_min": 22000, "salary_max": 38000, "min_years_experience": 1},
    {"title": "HR Coordinator", "salary_min": 18000, "salary_max": 30000},
    {"title": "HR Generalist", "salary_min": 22000, "salary_max": 38000},
    {"title": "HR Specialist", "salary_min": 25000, "salary_max": 45000},
    {"title": "Recruiter", "salary_min": 22000, "salary_max": 40000},
    {"title": "Talent Acquisition Specialist", "salary_min": 28000, "salary_max": 50000},
    {"title": "Compensation & Benefits Specialist", "salary_min": 28000, "salary_max": 50000},
    {"title": "Learning & Development Specialist", "salary_min": 25000, "salary_max": 45000},
    {"title": "HR Business Partner", "salary_min": 42000, "salary_max": 75000},
    {"title": "Senior Recruiter", "salary_min": 35000, "salary_max": 60000},
    {"title": "HR Manager", "salary_min": 50000, "salary_max": 90000, "seniority": "senior", "min_years_experience": 6, "category": "Management"},
    {"title": "HR Director", "salary_min": 100000, "salary_max": 160000},
    {"title": "CHRO", "salary_min": 120000, "salary_max": 250000},

    # ── Management ─────────────────────────────────────
    {"title": "Engineering Manager", "salary_min": 80000, "salary_max": 140000},
    {"title": "VP of Engineering", "salary_min": 140000, "salary_max": 280000},
    {"title": "Chief Technology Officer", "salary_min": 160000, "salary_max": 350000},
    {"title": "Director of Engineering", "salary_min": 110000, "salary_max": 200000},
    {"title": "Team Lead", "salary_min": 50000, "salary_max": 90000},
    {"title": "BPO Operations Manager", "salary_min": 70000, "salary_max": 120000, "seniority": "senior", "min_years_experience": 8},
    {"title": "Customer Success Manager", "salary_min": 35000, "salary_max": 60000, "seniority": "mid", "min_years_experience": 3},
    {"title": "FinTech Operations Manager", "salary_min": 70000, "salary_max": 120000, "seniority": "senior", "min_years_experience": 5},
    {"title": "Junior Project Manager", "salary_min": 22000, "salary_max": 35000},
    {"title": "Marketing Manager", "salary_min": 50000, "salary_max": 85000, "seniority": "senior", "min_years_experience": 5},
    {"title": "Office Manager", "salary_min": 35000, "salary_max": 60000, "seniority": "mid", "min_years_experience": 3},
    {"title": "Operations Director", "salary_min": 100000, "salary_max": 180000},
    {"title": "Project Manager", "salary_min": 50000, "salary_max": 90000, "seniority": "senior", "min_years_experience": 5},
    {"title": "QA Manager", "salary_min": 65000, "salary_max": 110000, "seniority": "senior", "min_years_experience": 6},
    {"title": "Sales Manager", "salary_min": 45000, "salary_max": 85000, "seniority": "senior", "min_years_experience": 5},
    {"title": "Senior Project Manager", "salary_min": 65000, "salary_max": 110000},
    {"title": "CMO", "salary_min": 100000, "salary_max": 200000},

    # ── Product ────────────────────────────────────────
    {"title": "Product Manager", "salary_min": 40000, "salary_max": 75000},
    {"title": "Senior Product Manager", "salary_min": 75000, "salary_max": 130000},
    {"title": "Product Owner", "salary_min": 40000, "salary_max": 75000},
    {"title": "Scrum Master", "salary_min": 35000, "salary_max": 70000},
    {"title": "Technical Program Manager", "salary_min": 60000, "salary_max": 120000},
    {"title": "Agile Coach", "salary_min": 55000, "salary_max": 95000, "seniority": "senior", "min_years_experience": 5},
    {"title": "Business Analyst", "salary_min": 28000, "salary_max": 50000},
    {"title": "Senior Business Analyst", "salary_min": 45000, "salary_max": 80000},
    {"title": "CPO", "salary_min": 150000, "salary_max": 300000},
    {"title": "Director of Product", "salary_min": 110000, "salary_max": 180000},
    {"title": "FinTech Product Manager", "salary_min": 55000, "salary_max": 100000, "seniority": "senior", "min_years_experience": 5},
    {"title": "Junior Product Manager", "salary_min": 22000, "salary_max": 35000},
    {"title": "Product Analyst", "salary_min": 28000, "salary_max": 50000},
    {"title": "Program Manager", "salary_min": 55000, "salary_max": 100000, "seniority": "senior", "min_years_experience": 5},
    {"title": "VP of Product", "salary_min": 120000, "salary_max": 250000},

    # ── BPO / Operations ──────────────────────────────
    {"title": "Customer Service Representative", "salary_min": 18000, "salary_max": 30000, "seniority": "entry", "min_years_experience": 1},
    {"title": "BPO Team Lead", "salary_min": 25000, "salary_max": 45000},
    {"title": "Quality Analyst", "salary_min": 20000, "salary_max": 35000},
    {"title": "BPO Operations Supervisor", "salary_min": 28000, "salary_max": 50000},
    {"title": "Customer Service Manager", "salary_min": 40000, "salary_max": 70000},
    {"title": "Operations Manager", "salary_min": 50000, "salary_max": 100000},
    {"title": "Quality Assurance Analyst", "salary_min": 25000, "salary_max": 40000},
    {"title": "Technical Support Specialist", "salary_min": 18000, "salary_max": 32000, "seniority": "entry", "min_years_experience": 1},
    {"title": "Workforce Analyst", "salary_min": 22000, "salary_max": 40000},

    # ── Marketing ──────────────────────────────────────
    {"title": "Digital Marketing Specialist", "salary_min": 25000, "salary_max": 45000},
    {"title": "Digital Marketing Manager", "salary_min": 45000, "salary_max": 80000},
    {"title": "SEO Specialist", "salary_min": 20000, "salary_max": 42000},
    {"title": "Director of Marketing", "salary_min": 100000, "salary_max": 180000},
    {"title": "Marketing Analyst", "salary_min": 25000, "salary_max": 40000},
    {"title": "Marketing Coordinator", "salary_min": 18000, "salary_max": 30000},
    {"title": "Content Strategist", "salary_min": 25000, "salary_max": 50000},
    {"title": "Senior Content Strategist", "salary_min": 38000, "salary_max": 70000},
    {"title": "Social Media Manager", "salary_min": 20000, "salary_max": 40000},
    {"title": "Email Marketing Specialist", "salary_min": 18000, "salary_max": 35000},
    {"title": "Growth Hacker", "salary_min": 30000, "salary_max": 60000},
    {"title": "Brand Manager", "salary_min": 38000, "salary_max": 70000},
    {"title": "Performance Marketing Manager", "salary_min": 40000, "salary_max": 75000},
    {"title": "Product Marketing Manager", "salary_min": 42000, "salary_max": 80000},
    {"title": "PR Specialist", "salary_min": 22000, "salary_max": 42000},

    # ── Sales ──────────────────────────────────────────
    {"title": "Sales Representative", "salary_min": 20000, "salary_max": 35000},
    {"title": "Director of Sales", "salary_min": 100000, "salary_max": 170000},
    {"title": "Business Development Representative", "salary_min": 20000, "salary_max": 35000},
    {"title": "Inside Sales Representative", "salary_min": 18000, "salary_max": 32000},
    {"title": "Sales Engineer", "salary_min": 35000, "salary_max": 65000},
    {"title": "Sales Operations Analyst", "salary_min": 25000, "salary_max": 45000},
    {"title": "Key Account Manager", "salary_min": 42000, "salary_max": 80000},
    {"title": "Regional Sales Manager", "salary_min": 55000, "salary_max": 100000},

    # ── Security ───────────────────────────────────────
    {"title": "CISO", "salary_min": 140000, "salary_max": 250000},
    {"title": "Cybersecurity Analyst", "salary_min": 38000, "salary_max": 65000},
    {"title": "Penetration Tester", "salary_min": 38000, "salary_max": 70000},
    {"title": "Security Consultant", "salary_min": 42000, "salary_max": 75000},
    {"title": "Junior Cybersecurity Analyst", "salary_min": 20000, "salary_max": 35000},

    # ── IT ─────────────────────────────────────────────
    {"title": "System Administrator", "salary_min": 25000, "salary_max": 50000},
    {"title": "Network Engineer", "salary_min": 28000, "salary_max": 55000},
    {"title": "Cloud Architect", "salary_min": 90000, "salary_max": 170000},
    {"title": "Cloud Engineer", "salary_min": 45000, "salary_max": 90000},
    {"title": "Security Engineer", "salary_min": 45000, "salary_max": 95000},
    {"title": "IT Manager", "salary_min": 50000, "salary_max": 95000},
    {"title": "Database Administrator", "category": "IT", "salary_min": 35000, "salary_max": 70000},
    {"title": "IT Director", "salary_min": 80000, "salary_max": 150000},
    {"title": "IT Help Desk Technician", "salary_min": 15000, "salary_max": 25000},
    {"title": "IT Support Specialist", "salary_min": 15000, "salary_max": 28000},
    {"title": "IT Project Manager", "salary_min": 60000, "salary_max": 100000, "seniority": "senior", "min_years_experience": 6},
    {"title": "IT Service Manager", "salary_min": 65000, "salary_max": 110000, "seniority": "senior", "min_years_experience": 6},
    {"title": "Senior System Administrator", "salary_min": 42000, "salary_max": 75000},

    # ── Consulting ─────────────────────────────────────
    {"title": "Management Consultant", "salary_min": 40000, "salary_max": 85000},
    {"title": "IT Consultant", "salary_min": 45000, "salary_max": 90000},
    {"title": "ERP Consultant", "salary_min": 50000, "salary_max": 100000},
    {"title": "Technical Consultant", "salary_min": 40000, "salary_max": 75000},
    {"title": "Technology Advisor", "salary_min": 80000, "salary_max": 160000},

    # ── Customer Success ───────────────────────────────
    {"title": "Customer Experience Manager", "salary_min": 38000, "salary_max": 65000},
    {"title": "Customer Success Specialist", "salary_min": 20000, "salary_max": 35000},
    {"title": "Support Team Lead", "salary_min": 28000, "salary_max": 48000},

    # ── Legal / Compliance ─────────────────────────────
    {"title": "Compliance Analyst", "salary_min": 28000, "salary_max": 50000},
    {"title": "Compliance Officer", "salary_min": 35000, "salary_max": 60000},
    {"title": "Data Privacy Officer", "salary_min": 50000, "salary_max": 90000},
    {"title": "Legal Counsel", "salary_min": 50000, "salary_max": 90000},

    # ── Content ────────────────────────────────────────
    {"title": "Content Writer", "salary_min": 18000, "salary_max": 32000},
    {"title": "Copywriter", "salary_min": 20000, "salary_max": 38000},

    # ── Education ──────────────────────────────────────
    {"title": "Instructional Designer", "salary_min": 25000, "salary_max": 45000},
    {"title": "Technical Trainer", "salary_min": 25000, "salary_max": 42000},

    # ── Operations ─────────────────────────────────────
    {"title": "Logistics Coordinator", "salary_min": 18000, "salary_max": 32000},
    {"title": "Procurement Specialist", "salary_min": 25000, "salary_max": 42000},
    {"title": "Supply Chain Analyst", "salary_min": 25000, "salary_max": 45000},

    # ── Engineering Junior ─────────────────────────────
    {"title": "Junior Software Developer", "salary_min": 20000, "salary_max": 35000},
    {"title": "Junior Backend Developer", "salary_min": 20000, "salary_max": 35000},
    {"title": "Junior Frontend Developer", "salary_min": 20000, "salary_max": 35000},
    {"title": "Junior Web Developer", "salary_min": 18000, "salary_max": 32000},
    {"title": "Junior QA Engineer", "salary_min": 18000, "salary_max": 30000},
    {"title": "Junior DevOps Engineer", "salary_min": 22000, "salary_max": 38000},
]


def main():
    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    roles = data["roles"]
    original_count = len(roles)

    # Step 1: Remove explicit duplicates by title
    roles = [r for r in roles if r["title"] not in REMOVE_TITLES]
    removed = original_count - len(roles)
    print(f"Removed {removed} duplicate roles by title")

    # Step 2: Remove second "Senior Financial Analyst" duplicate
    sfa_seen = False
    new_roles = []
    for r in roles:
        if r["title"] == "Senior Financial Analyst":
            if not sfa_seen:
                sfa_seen = True
                new_roles.append(r)
            else:
                print(f"  Removed duplicate: Senior Financial Analyst (second occurrence)")
                removed += 1
        else:
            new_roles.append(r)
    roles = new_roles

    # Step 3: Remove "Database Administrator" under Data (keep IT one)
    new_roles = []
    for r in roles:
        if r["title"] == "Database Administrator" and r.get("category") == "Data":
            print(f"  Removed duplicate: Database Administrator (Data category)")
            removed += 1
        else:
            new_roles.append(r)
    roles = new_roles

    # Step 4: Apply corrections
    corrected = 0
    for fix in CORRECTIONS:
        if fix.get("_remove"):
            continue  # already handled above

        title = fix["title"]
        category = fix.get("category")
        match_first = fix.get("_match_first", False)

        matched = False
        for r in roles:
            if r["title"] != title:
                continue
            if category and r.get("category") != category:
                continue

            # Apply salary corrections
            if "salary_min" in fix:
                sal_min = fix["salary_min"]
                sal_max = fix["salary_max"]
                r["salary_range_ph"] = f"PHP {sal_min:,} - {sal_max:,}"
                r["salary_range_usd"] = f"{format_usd(sal_min)} - {format_usd(sal_max)}"

            # Apply seniority corrections
            if "seniority" in fix:
                r["seniority"] = fix["seniority"]
            if "min_years_experience" in fix:
                r["min_years_experience"] = fix["min_years_experience"]

            corrected += 1
            matched = True
            if match_first:
                break  # only fix the first occurrence

        if not matched:
            print(f"  WARNING: No match for correction: {title}" + (f" ({category})" if category else ""))

    # Step 5: Update total count in metadata
    data["roles"] = roles
    data["metadata"]["total_roles"] = len(roles)

    # Step 6: Validate — check for remaining issues
    print(f"\nCorrected {corrected} salary/seniority entries")
    print(f"Final role count: {len(roles)} (was {original_count}, removed {removed})")

    # Check for any roles still with cookie-cutter ranges
    cookie_cutter_120k = [r["title"] for r in roles if r.get("salary_range_ph") == "PHP 120,000 - 300,000"]
    cookie_cutter_35k = [r["title"] for r in roles if r.get("salary_range_ph") == "PHP 35,000 - 65,000"]
    cookie_cutter_18k = [r["title"] for r in roles if r.get("salary_range_ph") == "PHP 18,000 - 35,000"]
    cookie_cutter_80k = [r["title"] for r in roles if r.get("salary_range_ph") == "PHP 80,000 - 150,000"]

    if cookie_cutter_120k:
        print(f"\n  Still have PHP 120k-300k: {cookie_cutter_120k}")
    if cookie_cutter_35k:
        print(f"  Still have PHP 35k-65k: {cookie_cutter_35k}")
    if cookie_cutter_80k:
        print(f"  Still have PHP 80k-150k: {cookie_cutter_80k}")

    # Check for duplicate titles
    from collections import Counter
    title_counts = Counter(r["title"] for r in roles)
    dupes = {t: c for t, c in title_counts.items() if c > 1}
    if dupes:
        print(f"\n  Remaining duplicate titles: {dupes}")

    with open(ROLES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\nDone! roles_ph.json updated.")


if __name__ == "__main__":
    main()
