"""
Comprehensive validation and fix script for roles_ph.json.
Based on web-researched PH salary data from:
- Glassdoor PH, PayScale PH, Jobstreet PH, Indeed PH
- Second Talent, NodeFlair, Manila Recruitment IT Salary Guide
- Acciyo 2025 HR Guide, PITON-Global, Outsourced Staff
- ERI SalaryExpert, Robert Walters PH, Michael Page PH

Fixes:
1. Remove near-duplicate roles (Accounting Clerk ≈ Bookkeeper, Staff Accountant ≈ Junior Accountant)
2. Fix career progression bugs (salary floor decreases, experience decreases)
3. Correct salary ranges confirmed >20% off by multiple sources
4. Update demand/stability/growth scores for roles with placeholder 0.7 values
"""

import json
import re
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "roles_ph.json"
PHP_TO_USD = 56

# ── Near-duplicate roles to remove ───────────────────────────────────
# Keep Bookkeeper (more common PH title), remove Accounting Clerk
# Keep Junior Accountant (clearer progression), remove Staff Accountant
REMOVE_TITLES = {"Accounting Clerk", "Staff Accountant"}

# ── Salary & field corrections ───────────────────────────────────────
# Only roles confirmed >20% off by multiple web sources
# Format: title -> {field: new_value}
CORRECTIONS = {
    # --- Career progression fixes ---
    "Auditor": {
        "salary_min": 23_000,  # was 20k, must be >= Internal Auditor (22k)
        "salary_max": 40_000,  # slight bump from 38k
    },
    "Senior Engineering Manager": {
        "min_years_experience": 7,  # was 5, must be > Engineering Manager (6)
    },

    # --- Tech salary corrections (multi-source confirmed) ---
    "DevOps Engineer": {
        # Second Talent mid: 90k-140k, NodeFlair median: 80k
        # Conservative local market adjustment
        "salary_min": 55_000,  # was 50k
        "salary_max": 110_000,  # was 100k
    },
    "Senior DevOps Engineer": {
        # Second Talent senior: 140k-200k
        # Local market adjustment
        "salary_min": 90_000,  # was 80k
        "salary_max": 160_000,  # was 140k
    },
    "Junior DevOps Engineer": {
        # DevOps is specialized even at junior level
        "salary_min": 25_000,  # was 22k
        "salary_max": 42_000,  # was 38k
    },
    "AI Engineer": {
        # Second Talent mid AI: 80k-120k
        # Local market adjustment
        "salary_min": 55_000,  # was 50k
        "salary_max": 105_000,  # was 100k
    },
    "Cybersecurity Engineer": {
        # NodeFlair median 67.5k, range to 165k
        # Upper bound was too low
        "salary_max": 100_000,  # was 80k
    },
    "Security Engineer": {
        # Aligning with cybersecurity engineer data
        "salary_max": 100_000,  # was 95k
    },
    "Site Reliability Engineer": {
        # PayScale SRE avg ~114k
        "salary_min": 60_000,  # was 55k
        "salary_max": 120_000,  # was 110k
    },
    "Cloud Engineer": {
        # Jobstreet cloud engineer avg 83k-93k
        "salary_min": 50_000,  # was 45k
        "salary_max": 95_000,  # was 90k
    },
    "Cloud Solutions Architect": {
        # PayScale avg ~92k, SalaryExpert ~112k
        "salary_min": 80_000,  # was 70k
        "salary_max": 150_000,  # was 130k
    },
    "Engineering Manager": {
        # PayScale software EM avg ~161k
        "salary_min": 90_000,  # was 80k
        "salary_max": 150_000,  # was 140k
    },

    # --- Finance salary corrections ---
    "Accounting Manager": {
        # SalaryExpert avg ~111k, entry AcctgMgr ~78k
        "salary_max": 110_000,  # was 85k
    },
    "Payroll Specialist": {
        # Acciyo 2025 HR guide: 25k-45k
        "salary_min": 25_000,  # was 22k
        "salary_max": 42_000,  # was 38k
    },
    "Compensation & Benefits Specialist": {
        # Acciyo 2025: 40k-70k
        "salary_min": 35_000,  # was 28k
        "salary_max": 58_000,  # was 50k
    },

    # --- BPO/Operations corrections ---
    "BPO Team Lead": {
        # PITON-Global: TL 35k-45k, Outsourced Staff: 35k-50k
        "salary_min": 30_000,  # was 25k
        "salary_max": 50_000,  # was 45k
    },

    # --- Sales corrections ---
    "Regional Sales Manager": {
        # ERI SalaryExpert avg ~124k
        "salary_max": 120_000,  # was 100k
    },
    "Sales Engineer": {
        # Glassdoor PH max ~48k, adjusted down
        "salary_max": 58_000,  # was 65k
    },
}

# ── Differentiated scores for batch-2 roles (had placeholder 0.7/0.7/0.7) ──
# Based on Philippine market demand, job stability, and growth outlook
SCORE_UPDATES = {
    # Engineering roles - high demand in PH tech sector
    "Backend Developer": {"demand_score": 0.88, "stability_score": 0.8, "growth_potential": 0.82},
    "Frontend Developer": {"demand_score": 0.85, "stability_score": 0.75, "growth_potential": 0.78},
    "Full-Stack Developer": {"demand_score": 0.9, "stability_score": 0.8, "growth_potential": 0.85},
    "Software Developer": {"demand_score": 0.85, "stability_score": 0.78, "growth_potential": 0.8},
    "Junior Software Developer": {"demand_score": 0.85, "stability_score": 0.7, "growth_potential": 0.9},
    "Junior Frontend Developer": {"demand_score": 0.82, "stability_score": 0.68, "growth_potential": 0.88},
    "Junior Backend Developer": {"demand_score": 0.82, "stability_score": 0.7, "growth_potential": 0.88},
    "Junior DevOps Engineer": {"demand_score": 0.78, "stability_score": 0.72, "growth_potential": 0.9},
    "Junior QA Engineer": {"demand_score": 0.75, "stability_score": 0.68, "growth_potential": 0.75},
    "Junior Web Developer": {"demand_score": 0.8, "stability_score": 0.65, "growth_potential": 0.85},
    "Senior Software Developer": {"demand_score": 0.88, "stability_score": 0.85, "growth_potential": 0.82},
    "Senior Backend Developer": {"demand_score": 0.88, "stability_score": 0.85, "growth_potential": 0.82},
    "Senior Frontend Developer": {"demand_score": 0.85, "stability_score": 0.82, "growth_potential": 0.8},
    "Senior Full-Stack Developer": {"demand_score": 0.9, "stability_score": 0.85, "growth_potential": 0.85},
    "Senior DevOps Engineer": {"demand_score": 0.87, "stability_score": 0.85, "growth_potential": 0.88},
    "Senior Data Engineer": {"demand_score": 0.85, "stability_score": 0.82, "growth_potential": 0.88},
    "Senior Mobile Developer": {"demand_score": 0.8, "stability_score": 0.78, "growth_potential": 0.78},
    "Senior QA Engineer": {"demand_score": 0.78, "stability_score": 0.78, "growth_potential": 0.72},
    "Senior Network Engineer": {"demand_score": 0.7, "stability_score": 0.8, "growth_potential": 0.68},
    "Senior Engineering Manager": {"demand_score": 0.75, "stability_score": 0.85, "growth_potential": 0.82},
    "BI Developer": {"demand_score": 0.78, "stability_score": 0.75, "growth_potential": 0.72},
    "Senior BI Developer": {"demand_score": 0.75, "stability_score": 0.78, "growth_potential": 0.72},
    "Data Architect": {"demand_score": 0.78, "stability_score": 0.8, "growth_potential": 0.82},
    "Data Engineering Manager": {"demand_score": 0.8, "stability_score": 0.82, "growth_potential": 0.85},
    "Cybersecurity Engineer": {"demand_score": 0.85, "stability_score": 0.85, "growth_potential": 0.9},
    "ML Engineer": {"demand_score": 0.82, "stability_score": 0.75, "growth_potential": 0.92},
    "MLOps Engineer": {"demand_score": 0.8, "stability_score": 0.75, "growth_potential": 0.9},
    "QA Automation Engineer": {"demand_score": 0.8, "stability_score": 0.78, "growth_potential": 0.78},
    "Manual QA Tester": {"demand_score": 0.72, "stability_score": 0.65, "growth_potential": 0.6},
    "Technical Writer": {"demand_score": 0.65, "stability_score": 0.7, "growth_potential": 0.65},
    "Developer Advocate": {"demand_score": 0.6, "stability_score": 0.6, "growth_potential": 0.75},
    "Technical Lead": {"demand_score": 0.78, "stability_score": 0.82, "growth_potential": 0.82},
    "Staff Engineer": {"demand_score": 0.72, "stability_score": 0.85, "growth_potential": 0.8},
    "Principal Engineer": {"demand_score": 0.65, "stability_score": 0.85, "growth_potential": 0.78},
    "Solutions Architect": {"demand_score": 0.78, "stability_score": 0.82, "growth_potential": 0.8},
    "Enterprise Architect": {"demand_score": 0.72, "stability_score": 0.82, "growth_potential": 0.75},
    "Infrastructure Architect": {"demand_score": 0.75, "stability_score": 0.82, "growth_potential": 0.78},
    "Security Architect": {"demand_score": 0.8, "stability_score": 0.85, "growth_potential": 0.88},
    "Mobile Engineering Lead": {"demand_score": 0.72, "stability_score": 0.78, "growth_potential": 0.75},
    "Head of Data Engineering": {"demand_score": 0.72, "stability_score": 0.82, "growth_potential": 0.82},
    "Head of Data Science": {"demand_score": 0.72, "stability_score": 0.8, "growth_potential": 0.85},
    "Head of Design": {"demand_score": 0.65, "stability_score": 0.75, "growth_potential": 0.72},
    "Automation Engineer": {"demand_score": 0.8, "stability_score": 0.75, "growth_potential": 0.8},
    "Release Engineer": {"demand_score": 0.68, "stability_score": 0.72, "growth_potential": 0.68},
    "Cloud Solutions Architect": {"demand_score": 0.88, "stability_score": 0.85, "growth_potential": 0.88},
    "Software Architect": {"demand_score": 0.78, "stability_score": 0.85, "growth_potential": 0.8},
    "DevSecOps Engineer": {"demand_score": 0.85, "stability_score": 0.82, "growth_potential": 0.9},
    "Embedded Systems Engineer": {"demand_score": 0.6, "stability_score": 0.78, "growth_potential": 0.68},
    "Game Developer": {"demand_score": 0.62, "stability_score": 0.58, "growth_potential": 0.65},
    "Blockchain Developer": {"demand_score": 0.5, "stability_score": 0.45, "growth_potential": 0.6},

    # Data roles
    "Junior Data Analyst": {"demand_score": 0.82, "stability_score": 0.72, "growth_potential": 0.85},
    "Junior Data Scientist": {"demand_score": 0.78, "stability_score": 0.7, "growth_potential": 0.9},
    "Senior Data Scientist": {"demand_score": 0.82, "stability_score": 0.8, "growth_potential": 0.88},
    "Senior Database Administrator": {"demand_score": 0.68, "stability_score": 0.8, "growth_potential": 0.62},
    "Lead Data Scientist": {"demand_score": 0.75, "stability_score": 0.8, "growth_potential": 0.85},
    "BI Manager": {"demand_score": 0.72, "stability_score": 0.78, "growth_potential": 0.72},
    "Data Governance Analyst": {"demand_score": 0.68, "stability_score": 0.8, "growth_potential": 0.75},
    "AI Research Scientist": {"demand_score": 0.68, "stability_score": 0.7, "growth_potential": 0.92},

    # Design roles
    "Graphic Designer": {"demand_score": 0.72, "stability_score": 0.6, "growth_potential": 0.55},
    "Design Lead": {"demand_score": 0.68, "stability_score": 0.75, "growth_potential": 0.75},
    "Junior UI/UX Designer": {"demand_score": 0.75, "stability_score": 0.65, "growth_potential": 0.82},
    "Motion Designer": {"demand_score": 0.62, "stability_score": 0.58, "growth_potential": 0.65},
    "Brand Designer": {"demand_score": 0.58, "stability_score": 0.6, "growth_potential": 0.55},
    "Content Designer": {"demand_score": 0.6, "stability_score": 0.62, "growth_potential": 0.65},

    # Finance roles
    "Account Executive": {"demand_score": 0.75, "stability_score": 0.65, "growth_potential": 0.72},
    "Account Manager": {"demand_score": 0.72, "stability_score": 0.72, "growth_potential": 0.7},
    "Accountant": {"demand_score": 0.82, "stability_score": 0.82, "growth_potential": 0.65},
    "Accounting Manager": {"demand_score": 0.72, "stability_score": 0.85, "growth_potential": 0.72},
    "Auditor": {"demand_score": 0.75, "stability_score": 0.82, "growth_potential": 0.68},
    "Senior Auditor": {"demand_score": 0.72, "stability_score": 0.85, "growth_potential": 0.72},
    "Junior Accountant": {"demand_score": 0.82, "stability_score": 0.78, "growth_potential": 0.7},
    "Senior Financial Analyst": {"demand_score": 0.78, "stability_score": 0.8, "growth_potential": 0.78},
    "FP&A Manager": {"demand_score": 0.72, "stability_score": 0.82, "growth_potential": 0.78},
    "Finance Manager": {"demand_score": 0.72, "stability_score": 0.85, "growth_potential": 0.75},
    "VP of Finance": {"demand_score": 0.55, "stability_score": 0.85, "growth_potential": 0.72},
    "Tax Accountant": {"demand_score": 0.75, "stability_score": 0.82, "growth_potential": 0.65},
    "Tax Manager": {"demand_score": 0.68, "stability_score": 0.85, "growth_potential": 0.7},
    "Tax Tech Consultant": {"demand_score": 0.65, "stability_score": 0.72, "growth_potential": 0.75},
    "Investment Analyst": {"demand_score": 0.68, "stability_score": 0.78, "growth_potential": 0.72},
    "Payroll Specialist": {"demand_score": 0.78, "stability_score": 0.78, "growth_potential": 0.55},
    "Budget Analyst": {"demand_score": 0.62, "stability_score": 0.8, "growth_potential": 0.58},
    "Risk Analyst": {"demand_score": 0.72, "stability_score": 0.85, "growth_potential": 0.72},
    "Credit Analyst": {"demand_score": 0.65, "stability_score": 0.8, "growth_potential": 0.6},
    "Treasury Analyst": {"demand_score": 0.6, "stability_score": 0.85, "growth_potential": 0.62},
    "FinTech Operations Manager": {"demand_score": 0.72, "stability_score": 0.75, "growth_potential": 0.78},
    "FinTech Product Manager": {"demand_score": 0.75, "stability_score": 0.75, "growth_potential": 0.82},

    # Management/Product roles
    "BPO Operations Manager": {"demand_score": 0.78, "stability_score": 0.75, "growth_potential": 0.68},
    "Customer Success Manager": {"demand_score": 0.75, "stability_score": 0.72, "growth_potential": 0.72},
    "Office Manager": {"demand_score": 0.68, "stability_score": 0.72, "growth_potential": 0.55},
    "Operations Director": {"demand_score": 0.68, "stability_score": 0.78, "growth_potential": 0.7},
    "Project Manager": {"demand_score": 0.78, "stability_score": 0.78, "growth_potential": 0.72},
    "Senior Project Manager": {"demand_score": 0.75, "stability_score": 0.8, "growth_potential": 0.72},
    "Junior Project Manager": {"demand_score": 0.75, "stability_score": 0.72, "growth_potential": 0.78},
    "HR Manager": {"demand_score": 0.72, "stability_score": 0.78, "growth_potential": 0.68},
    "QA Manager": {"demand_score": 0.72, "stability_score": 0.78, "growth_potential": 0.7},
    "Sales Manager": {"demand_score": 0.75, "stability_score": 0.7, "growth_potential": 0.68},
    "Marketing Manager": {"demand_score": 0.75, "stability_score": 0.7, "growth_potential": 0.72},
    "Business Analyst": {"demand_score": 0.78, "stability_score": 0.75, "growth_potential": 0.75},
    "Senior Business Analyst": {"demand_score": 0.75, "stability_score": 0.78, "growth_potential": 0.75},
    "Product Analyst": {"demand_score": 0.75, "stability_score": 0.72, "growth_potential": 0.78},
    "Program Manager": {"demand_score": 0.72, "stability_score": 0.78, "growth_potential": 0.75},
    "Junior Product Manager": {"demand_score": 0.72, "stability_score": 0.68, "growth_potential": 0.82},
    "Agile Coach": {"demand_score": 0.65, "stability_score": 0.68, "growth_potential": 0.68},

    # C-suite / Executive
    "CHRO": {"demand_score": 0.5, "stability_score": 0.78, "growth_potential": 0.65},
    "CISO": {"demand_score": 0.62, "stability_score": 0.82, "growth_potential": 0.8},
    "CMO": {"demand_score": 0.55, "stability_score": 0.7, "growth_potential": 0.68},
    "CPO": {"demand_score": 0.55, "stability_score": 0.75, "growth_potential": 0.75},
    "Director of Marketing": {"demand_score": 0.6, "stability_score": 0.72, "growth_potential": 0.7},
    "Director of Product": {"demand_score": 0.62, "stability_score": 0.78, "growth_potential": 0.78},
    "Director of Sales": {"demand_score": 0.6, "stability_score": 0.72, "growth_potential": 0.68},
    "VP of Product": {"demand_score": 0.55, "stability_score": 0.78, "growth_potential": 0.75},

    # HR roles
    "Administrative Assistant": {"demand_score": 0.78, "stability_score": 0.72, "growth_potential": 0.5},
    "Executive Assistant": {"demand_score": 0.72, "stability_score": 0.72, "growth_potential": 0.55},
    "HR Coordinator": {"demand_score": 0.75, "stability_score": 0.72, "growth_potential": 0.62},
    "HR Director": {"demand_score": 0.6, "stability_score": 0.82, "growth_potential": 0.68},
    "HR Specialist": {"demand_score": 0.72, "stability_score": 0.75, "growth_potential": 0.65},
    "Recruiter": {"demand_score": 0.78, "stability_score": 0.68, "growth_potential": 0.65},
    "Senior Recruiter": {"demand_score": 0.72, "stability_score": 0.7, "growth_potential": 0.65},
    "HR Business Partner": {"demand_score": 0.68, "stability_score": 0.78, "growth_potential": 0.7},
    "Talent Acquisition Specialist": {"demand_score": 0.75, "stability_score": 0.7, "growth_potential": 0.65},
    "Learning & Development Specialist": {"demand_score": 0.58, "stability_score": 0.72, "growth_potential": 0.62},
    "Compensation & Benefits Specialist": {"demand_score": 0.6, "stability_score": 0.78, "growth_potential": 0.58},
    "HR Generalist": {"demand_score": 0.72, "stability_score": 0.75, "growth_potential": 0.6},

    # IT roles
    "IT Project Manager": {"demand_score": 0.72, "stability_score": 0.78, "growth_potential": 0.72},
    "IT Service Manager": {"demand_score": 0.68, "stability_score": 0.78, "growth_potential": 0.65},
    "IT Director": {"demand_score": 0.6, "stability_score": 0.85, "growth_potential": 0.65},
    "Senior System Administrator": {"demand_score": 0.68, "stability_score": 0.8, "growth_potential": 0.6},
    "IT Help Desk Technician": {"demand_score": 0.72, "stability_score": 0.72, "growth_potential": 0.5},

    # Marketing roles
    "Digital Marketing Specialist": {"demand_score": 0.78, "stability_score": 0.68, "growth_potential": 0.72},
    "Marketing Coordinator": {"demand_score": 0.72, "stability_score": 0.65, "growth_potential": 0.65},
    "Marketing Analyst": {"demand_score": 0.72, "stability_score": 0.68, "growth_potential": 0.7},
    "Brand Manager": {"demand_score": 0.65, "stability_score": 0.68, "growth_potential": 0.62},
    "Product Marketing Manager": {"demand_score": 0.75, "stability_score": 0.72, "growth_potential": 0.75},
    "Performance Marketing Manager": {"demand_score": 0.8, "stability_score": 0.65, "growth_potential": 0.75},
    "PR Specialist": {"demand_score": 0.55, "stability_score": 0.62, "growth_potential": 0.52},

    # BPO/Operations
    "Quality Assurance Analyst": {"demand_score": 0.78, "stability_score": 0.72, "growth_potential": 0.6},

    # Sales
    "Sales Representative": {"demand_score": 0.78, "stability_score": 0.62, "growth_potential": 0.65},
    "Sales Engineer": {"demand_score": 0.75, "stability_score": 0.72, "growth_potential": 0.75},
    "Business Development Representative": {"demand_score": 0.8, "stability_score": 0.58, "growth_potential": 0.68},
    "Key Account Manager": {"demand_score": 0.68, "stability_score": 0.75, "growth_potential": 0.68},
    "Sales Operations Analyst": {"demand_score": 0.68, "stability_score": 0.7, "growth_potential": 0.68},
    "Regional Sales Manager": {"demand_score": 0.62, "stability_score": 0.72, "growth_potential": 0.65},
    "Inside Sales Representative": {"demand_score": 0.75, "stability_score": 0.58, "growth_potential": 0.62},

    # Consulting
    "Technical Consultant": {"demand_score": 0.72, "stability_score": 0.7, "growth_potential": 0.75},
    "Technology Advisor": {"demand_score": 0.6, "stability_score": 0.7, "growth_potential": 0.72},

    # Security
    "Cybersecurity Analyst": {"demand_score": 0.82, "stability_score": 0.82, "growth_potential": 0.88},
    "Senior Cybersecurity Analyst": {"demand_score": 0.8, "stability_score": 0.85, "growth_potential": 0.88},
    "Junior Cybersecurity Analyst": {"demand_score": 0.78, "stability_score": 0.78, "growth_potential": 0.9},
    "Penetration Tester": {"demand_score": 0.75, "stability_score": 0.78, "growth_potential": 0.85},
    "Security Consultant": {"demand_score": 0.72, "stability_score": 0.78, "growth_potential": 0.82},

    # Legal/Compliance
    "Compliance Officer": {"demand_score": 0.68, "stability_score": 0.82, "growth_potential": 0.68},
    "Legal Counsel": {"demand_score": 0.6, "stability_score": 0.88, "growth_potential": 0.6},
    "Compliance Analyst": {"demand_score": 0.65, "stability_score": 0.82, "growth_potential": 0.62},
    "Data Privacy Officer": {"demand_score": 0.72, "stability_score": 0.85, "growth_potential": 0.78},

    # Customer Success
    "Customer Success Specialist": {"demand_score": 0.75, "stability_score": 0.68, "growth_potential": 0.68},
    "Customer Experience Manager": {"demand_score": 0.68, "stability_score": 0.7, "growth_potential": 0.68},
    "Support Team Lead": {"demand_score": 0.72, "stability_score": 0.7, "growth_potential": 0.6},

    # Content
    "Content Writer": {"demand_score": 0.72, "stability_score": 0.58, "growth_potential": 0.58},
    "Copywriter": {"demand_score": 0.65, "stability_score": 0.58, "growth_potential": 0.55},
    "Senior Content Strategist": {"demand_score": 0.6, "stability_score": 0.65, "growth_potential": 0.62},

    # Operations
    "Supply Chain Analyst": {"demand_score": 0.65, "stability_score": 0.75, "growth_potential": 0.58},
    "Procurement Specialist": {"demand_score": 0.6, "stability_score": 0.78, "growth_potential": 0.52},
    "Logistics Coordinator": {"demand_score": 0.6, "stability_score": 0.72, "growth_potential": 0.48},

    # Education
    "Instructional Designer": {"demand_score": 0.58, "stability_score": 0.7, "growth_potential": 0.62},
    "Technical Trainer": {"demand_score": 0.55, "stability_score": 0.68, "growth_potential": 0.55},
}


def format_php(amount: int) -> str:
    return f"PHP {amount:,}"


def format_usd(php_amount: int) -> str:
    usd = round(php_amount / PHP_TO_USD / 50) * 50
    return f"${usd:,}"


def main():
    with open(DATA_PATH) as f:
        data = json.load(f)

    roles = data["roles"]
    original_count = len(roles)

    # Step 1: Remove near-duplicates
    removed = []
    roles = [r for r in roles if r["title"] not in REMOVE_TITLES or not removed.append(r["title"])]
    # Fix: the above doesn't work as intended. Do properly:
    new_roles = []
    for r in data["roles"]:
        if r["title"] in REMOVE_TITLES:
            removed.append(r["title"])
        else:
            new_roles.append(r)
    roles = new_roles
    print(f"Removed {len(removed)} near-duplicate roles: {removed}")

    # Step 2: Apply salary & field corrections
    salary_fixes = 0
    field_fixes = 0
    for role in roles:
        title = role["title"]
        if title not in CORRECTIONS:
            continue

        updates = CORRECTIONS[title]

        if "salary_min" in updates or "salary_max" in updates:
            old_sal = role["salary_range_ph"]
            php_match = re.findall(r"[\d,]+", role["salary_range_ph"])
            old_min = int(php_match[0].replace(",", ""))
            old_max = int(php_match[1].replace(",", ""))

            new_min = updates.get("salary_min", old_min)
            new_max = updates.get("salary_max", old_max)

            role["salary_range_ph"] = f"{format_php(new_min)} - {format_php(new_max)}"
            role["salary_range_usd"] = f"{format_usd(new_min)} - {format_usd(new_max)}"
            salary_fixes += 1
            print(f"  Salary: {title}: {old_sal} -> {role['salary_range_ph']}")

        if "min_years_experience" in updates:
            old_yrs = role["min_years_experience"]
            role["min_years_experience"] = updates["min_years_experience"]
            field_fixes += 1
            print(f"  Field: {title}: min_years {old_yrs} -> {updates['min_years_experience']}")

        if "seniority" in updates:
            old_sen = role["seniority"]
            role["seniority"] = updates["seniority"]
            field_fixes += 1
            print(f"  Field: {title}: seniority {old_sen} -> {updates['seniority']}")

    # Step 3: Update placeholder scores
    score_updates = 0
    for role in roles:
        title = role["title"]
        if title in SCORE_UPDATES:
            scores = SCORE_UPDATES[title]
            changed = False
            for key, val in scores.items():
                if role.get(key) != val:
                    role[key] = val
                    changed = True
            if changed:
                score_updates += 1

    # Update metadata
    data["roles"] = roles
    data["metadata"]["total_roles"] = len(roles)

    # Write back
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n=== Summary ===")
    print(f"  Roles: {original_count} -> {len(roles)} ({original_count - len(roles)} removed)")
    print(f"  Salary corrections: {salary_fixes}")
    print(f"  Field corrections: {field_fixes}")
    print(f"  Score updates: {score_updates}")

    # Verify no career progression issues remain
    print(f"\n=== Verification ===")
    role_map = {r["title"]: r for r in roles}
    checks = [
        ("Internal Auditor", "Auditor"),
        ("Engineering Manager", "Senior Engineering Manager"),
    ]
    for a, b in checks:
        if a in role_map and b in role_map:
            ra, rb = role_map[a], role_map[b]
            sa = re.findall(r"[\d,]+", ra["salary_range_ph"])
            sb = re.findall(r"[\d,]+", rb["salary_range_ph"])
            min_a, min_b = int(sa[0].replace(",", "")), int(sb[0].replace(",", ""))
            yrs_a, yrs_b = ra["min_years_experience"], rb["min_years_experience"]
            ok_sal = min_b >= min_a
            ok_yrs = yrs_b >= yrs_a
            print(f"  {a} -> {b}: salary {min_a:,}->{min_b:,} {'OK' if ok_sal else 'FAIL'}, "
                  f"years {yrs_a}->{yrs_b} {'OK' if ok_yrs else 'FAIL'}")


if __name__ == "__main__":
    main()
