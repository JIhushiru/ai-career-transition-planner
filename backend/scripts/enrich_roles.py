"""One-time script to enrich roles that have empty required_skills/preferred_skills."""

import json
from pathlib import Path

ROLES_FILE = Path(__file__).parent.parent / "app" / "data" / "roles_ph.json"

# ──────────────────────────────────────────────────────
# Skills & descriptions for every incomplete role
# Keyed by exact title as it appears in roles_ph.json
# ──────────────────────────────────────────────────────
ENRICHMENT: dict[str, dict] = {
    # ── BPO / Operations ──────────────────────────────
    "Customer Service Representative": {
        "description": "Handles customer inquiries and complaints via phone, email, and chat. Resolves issues, processes orders, and ensures customer satisfaction while meeting KPI targets in a fast-paced BPO environment.",
        "required_skills": ["Customer Service", "Communication", "CRM Software", "Problem-Solving", "Conflict Resolution"],
        "preferred_skills": ["Zendesk", "Salesforce", "Live Chat", "Quality Assurance", "Upselling"],
    },
    "Quality Assurance Analyst": {
        "description": "Monitors and evaluates BPO agent performance through call monitoring, ticket audits, and quality scorecards. Identifies training gaps and drives process improvements to maintain service excellence.",
        "required_skills": ["Quality Monitoring", "Data Analysis", "Communication", "Process Improvement", "Reporting"],
        "preferred_skills": ["NICE inContact", "Verint", "Six Sigma", "Calibration", "Root Cause Analysis"],
    },

    # ── Consulting ────────────────────────────────────
    "Technical Consultant": {
        "description": "Advises clients on technology solutions and system architecture. Translates business requirements into technical designs, leads implementations, and provides expert guidance on best practices.",
        "required_skills": ["Requirements Analysis", "Solution Architecture", "Client Management", "Technical Documentation", "Problem-Solving"],
        "preferred_skills": ["Cloud Architecture", "Enterprise Integration", "Agile", "Pre-Sales", "Change Management"],
    },

    # ── Data ──────────────────────────────────────────
    "AI Research Scientist": {
        "description": "Conducts original research in machine learning and artificial intelligence. Develops novel algorithms, publishes findings, and translates research into production-ready models.",
        "required_skills": ["Machine Learning", "Deep Learning", "Python", "PyTorch", "Statistics", "Linear Algebra"],
        "preferred_skills": ["NLP", "Computer Vision", "Reinforcement Learning", "Research Publication", "TensorFlow"],
    },
    "BI Manager": {
        "description": "Leads the business intelligence team and strategy. Oversees data warehouse architecture, reporting frameworks, and analytics delivery to drive data-informed decision-making across the organization.",
        "required_skills": ["Business Intelligence", "SQL", "Data Warehousing", "Team Leadership", "Strategic Planning", "Stakeholder Management"],
        "preferred_skills": ["Power BI", "Tableau", "ETL", "Data Governance", "Budgeting"],
    },
    "Head of Data Science": {
        "description": "Directs the data science function and sets the analytics strategy. Builds and leads high-performing teams, defines ML/AI roadmaps, and ensures data science delivers measurable business impact.",
        "required_skills": ["Machine Learning", "Python", "Statistical Modeling", "Team Leadership", "Strategic Planning", "Stakeholder Management"],
        "preferred_skills": ["Deep Learning", "MLOps", "Cloud Platforms", "A/B Testing", "Executive Communication"],
    },
    "Senior Data Scientist": {
        "description": "Leads complex data science projects from problem framing through deployment. Builds predictive models, mentors junior scientists, and partners with stakeholders to solve high-impact business problems.",
        "required_skills": ["Python", "Machine Learning", "SQL", "Statistical Modeling", "Data Visualization", "Feature Engineering"],
        "preferred_skills": ["Deep Learning", "Spark", "MLOps", "A/B Testing", "Scikit-learn"],
    },
    "Senior Database Administrator": {
        "description": "Manages and optimizes enterprise database systems for performance, availability, and security. Leads database architecture decisions, disaster recovery planning, and capacity management.",
        "required_skills": ["SQL", "Database Administration", "Performance Tuning", "Backup & Recovery", "Database Security"],
        "preferred_skills": ["PostgreSQL", "MySQL", "Oracle", "MongoDB", "Cloud Databases", "Replication"],
    },

    # ── Design ────────────────────────────────────────
    "Design Lead": {
        "description": "Leads a team of designers and sets design direction for products. Establishes design systems, reviews work quality, and ensures designs meet user needs and business objectives.",
        "required_skills": ["UI/UX Design", "Design Systems", "Team Leadership", "Figma", "User Research", "Prototyping"],
        "preferred_skills": ["Design Thinking", "Accessibility", "Motion Design", "Design Ops", "Mentoring"],
    },
    "Graphic Designer": {
        "description": "Creates visual content for marketing, branding, and digital platforms. Designs graphics, layouts, and illustrations that communicate brand identity and engage target audiences.",
        "required_skills": ["Adobe Photoshop", "Adobe Illustrator", "Typography", "Layout Design", "Brand Identity"],
        "preferred_skills": ["Figma", "After Effects", "Print Design", "Social Media Graphics", "Photography"],
    },
    "Head of Design": {
        "description": "Oversees the entire design organization and sets the design vision. Defines design culture, hires and develops talent, and ensures design excellence across all products and touchpoints.",
        "required_skills": ["Design Strategy", "Team Leadership", "UI/UX Design", "Stakeholder Management", "Design Systems", "Hiring"],
        "preferred_skills": ["Design Thinking", "Organizational Design", "Executive Communication", "Budgeting", "Cross-Functional Leadership"],
    },

    # ── Engineering ───────────────────────────────────
    "Backend Developer": {
        "description": "Builds and maintains server-side applications, APIs, and database integrations. Writes clean, performant code and ensures system reliability and scalability.",
        "required_skills": ["Python", "SQL", "REST APIs", "Git", "Database Design"],
        "preferred_skills": ["Node.js", "Docker", "Redis", "Message Queues", "GraphQL"],
    },
    "BI Developer": {
        "description": "Designs and develops business intelligence solutions including dashboards, reports, and data pipelines. Transforms raw data into actionable insights for business stakeholders.",
        "required_skills": ["SQL", "Power BI", "Data Warehousing", "ETL", "Data Modeling"],
        "preferred_skills": ["Tableau", "Python", "SSIS", "DAX", "Stored Procedures"],
    },
    "CTO": {
        "description": "Sets the technology vision and strategy for the organization. Leads engineering teams, makes architecture decisions, manages technical debt, and ensures technology drives business growth.",
        "required_skills": ["Software Architecture", "Team Leadership", "Strategic Planning", "Cloud Architecture", "Stakeholder Management", "Budgeting"],
        "preferred_skills": ["DevOps", "Microservices", "Security", "Vendor Management", "Board Communication"],
    },
    "Cybersecurity Engineer": {
        "description": "Designs and implements security solutions to protect systems, networks, and data. Conducts vulnerability assessments, builds security tools, and responds to security incidents.",
        "required_skills": ["Network Security", "Vulnerability Assessment", "Firewall Management", "SIEM", "Incident Response"],
        "preferred_skills": ["Penetration Testing", "Python", "Cloud Security", "IDS/IPS", "Cryptography"],
    },
    "Data Architect": {
        "description": "Designs enterprise data architecture including data models, data flows, and integration patterns. Defines standards for data storage, access, and governance across the organization.",
        "required_skills": ["Data Modeling", "SQL", "Data Warehousing", "ETL", "Database Design", "Data Governance"],
        "preferred_skills": ["Cloud Platforms", "Spark", "Data Lake", "Kafka", "Enterprise Architecture"],
    },
    "Data Engineering Manager": {
        "description": "Leads data engineering teams and oversees the design and maintenance of data infrastructure. Sets technical direction for data pipelines, platforms, and tooling.",
        "required_skills": ["Data Engineering", "Python", "SQL", "Team Leadership", "Data Architecture", "Cloud Platforms"],
        "preferred_skills": ["Spark", "Airflow", "Kafka", "Data Governance", "Budgeting"],
    },
    "Developer Advocate": {
        "description": "Bridges the gap between developer communities and the company's products. Creates technical content, speaks at conferences, builds demos, and gathers developer feedback to improve products.",
        "required_skills": ["Technical Writing", "Public Speaking", "Programming", "Developer Tools", "Community Building"],
        "preferred_skills": ["JavaScript", "Python", "Content Creation", "Social Media", "Open Source"],
    },
    "Enterprise Architect": {
        "description": "Defines the overall IT architecture strategy aligned with business goals. Creates blueprints for systems integration, technology standards, and modernization roadmaps.",
        "required_skills": ["Enterprise Architecture", "Solution Architecture", "Cloud Architecture", "TOGAF", "Stakeholder Management", "Systems Integration"],
        "preferred_skills": ["Microservices", "API Design", "Security Architecture", "Business Analysis", "Vendor Management"],
    },
    "Frontend Developer": {
        "description": "Develops user-facing web applications with modern JavaScript frameworks. Focuses on responsive design, accessibility, and optimal user experience.",
        "required_skills": ["JavaScript", "HTML", "CSS", "React", "Git"],
        "preferred_skills": ["TypeScript", "Next.js", "Tailwind CSS", "Testing", "Accessibility"],
    },
    "Full-Stack Developer": {
        "description": "Builds complete web applications handling both frontend and backend development. Works across the entire stack from user interface to database and deployment.",
        "required_skills": ["JavaScript", "HTML", "CSS", "Node.js", "SQL", "React", "Git"],
        "preferred_skills": ["TypeScript", "Docker", "REST APIs", "MongoDB", "CI/CD"],
    },
    "Head of Data Engineering": {
        "description": "Directs the data engineering organization and sets the technical strategy for data infrastructure. Oversees data platform architecture, team growth, and cross-functional data initiatives.",
        "required_skills": ["Data Engineering", "Team Leadership", "Data Architecture", "Cloud Platforms", "Strategic Planning", "Stakeholder Management"],
        "preferred_skills": ["Spark", "Kafka", "Data Governance", "Budgeting", "Executive Communication"],
    },
    "Infrastructure Architect": {
        "description": "Designs and plans enterprise infrastructure including cloud, networking, and compute resources. Ensures systems meet performance, security, and scalability requirements.",
        "required_skills": ["Cloud Architecture", "Networking", "Linux", "Infrastructure as Code", "Security", "Disaster Recovery"],
        "preferred_skills": ["AWS", "Terraform", "Kubernetes", "Monitoring", "Cost Optimization"],
    },
    "Junior Backend Developer": {
        "description": "Assists in building server-side applications and APIs under senior guidance. Learns backend development practices, writes code, fixes bugs, and participates in code reviews.",
        "required_skills": ["Python", "SQL", "REST APIs", "Git"],
        "preferred_skills": ["Node.js", "Docker", "Database Basics", "Testing"],
    },
    "Junior DevOps Engineer": {
        "description": "Supports CI/CD pipelines, infrastructure automation, and deployment processes. Learns DevOps practices while assisting with monitoring, scripting, and cloud resource management.",
        "required_skills": ["Linux", "Git", "Bash", "CI/CD Basics", "Cloud Basics"],
        "preferred_skills": ["Docker", "AWS", "Python", "Monitoring", "Networking"],
    },
    "Junior Frontend Developer": {
        "description": "Builds user interfaces for web applications under senior guidance. Implements designs in HTML/CSS/JavaScript and learns modern frontend frameworks and best practices.",
        "required_skills": ["HTML", "CSS", "JavaScript", "Git"],
        "preferred_skills": ["React", "TypeScript", "Responsive Design", "Testing"],
    },
    "Junior QA Engineer": {
        "description": "Assists in software testing by executing test cases, reporting bugs, and verifying fixes. Learns quality assurance methodologies and testing tools under senior guidance.",
        "required_skills": ["Manual Testing", "Bug Reporting", "Test Case Writing", "Communication"],
        "preferred_skills": ["SQL", "API Testing", "Jira", "Agile"],
    },
    "Junior Web Developer": {
        "description": "Develops and maintains websites and web applications under senior guidance. Builds pages, fixes bugs, and learns full-stack web development practices.",
        "required_skills": ["HTML", "CSS", "JavaScript", "Git"],
        "preferred_skills": ["React", "PHP", "WordPress", "Responsive Design"],
    },
    "ML Engineer": {
        "description": "Builds and deploys machine learning models into production systems. Designs ML pipelines, optimizes model performance, and bridges the gap between data science and engineering.",
        "required_skills": ["Python", "Machine Learning", "TensorFlow", "SQL", "Docker", "Data Pipelines"],
        "preferred_skills": ["PyTorch", "Kubernetes", "MLOps", "Feature Engineering", "Cloud Platforms"],
    },
    "MLOps Engineer": {
        "description": "Builds and maintains the infrastructure for deploying, monitoring, and scaling machine learning models. Automates ML pipelines and ensures model reliability in production.",
        "required_skills": ["Python", "Docker", "Kubernetes", "CI/CD", "ML Pipelines", "Cloud Platforms"],
        "preferred_skills": ["MLflow", "Airflow", "Terraform", "Monitoring", "Model Serving"],
    },
    "Manual QA Tester": {
        "description": "Executes manual test cases to verify software quality. Identifies bugs, documents defects, performs regression testing, and ensures features meet acceptance criteria.",
        "required_skills": ["Manual Testing", "Test Case Design", "Bug Reporting", "Regression Testing", "Communication"],
        "preferred_skills": ["SQL", "API Testing", "Jira", "Agile", "Mobile Testing"],
    },
    "QA Automation Engineer": {
        "description": "Designs and implements automated test frameworks and scripts. Integrates automated tests into CI/CD pipelines and reduces manual testing effort while improving coverage.",
        "required_skills": ["Test Automation", "Selenium", "Python", "CI/CD", "Test Framework Design"],
        "preferred_skills": ["Cypress", "JavaScript", "API Testing", "Performance Testing", "Docker"],
    },
    "Senior BI Developer": {
        "description": "Leads BI solution development including complex dashboards, data models, and ETL processes. Mentors junior developers and architects scalable business intelligence platforms.",
        "required_skills": ["SQL", "Power BI", "Data Warehousing", "ETL", "Data Modeling", "Stakeholder Management"],
        "preferred_skills": ["Tableau", "Python", "DAX", "Azure", "Performance Optimization"],
    },
    "Senior Backend Developer": {
        "description": "Leads backend development of complex systems and APIs. Makes architecture decisions, mentors junior developers, and ensures code quality, scalability, and performance.",
        "required_skills": ["Python", "SQL", "REST APIs", "System Design", "Git", "Database Design"],
        "preferred_skills": ["Node.js", "Docker", "Kubernetes", "Microservices", "Message Queues", "Redis"],
    },
    "Senior Cybersecurity Analyst": {
        "description": "Leads security operations and threat analysis. Conducts advanced incident response, develops security strategies, and mentors junior analysts on emerging threats and defense techniques.",
        "required_skills": ["Threat Analysis", "Incident Response", "SIEM", "Vulnerability Management", "Network Security", "Security Operations"],
        "preferred_skills": ["Forensics", "Malware Analysis", "Cloud Security", "Compliance", "Python"],
    },
    "Senior Data Engineer": {
        "description": "Designs and builds scalable data pipelines and infrastructure. Leads data platform architecture decisions, optimizes data processing, and mentors junior engineers.",
        "required_skills": ["Python", "SQL", "Spark", "Data Pipelines", "Cloud Platforms", "Data Modeling"],
        "preferred_skills": ["Kafka", "Airflow", "Data Lake", "Terraform", "Performance Optimization"],
    },
    "Senior DevOps Engineer": {
        "description": "Leads DevOps practices and infrastructure automation. Designs CI/CD pipelines, manages cloud infrastructure, and drives reliability and deployment efficiency across teams.",
        "required_skills": ["Linux", "Docker", "Kubernetes", "CI/CD", "Cloud Platforms", "Infrastructure as Code"],
        "preferred_skills": ["Terraform", "AWS", "Monitoring", "Python", "Security"],
    },
    "Senior Engineering Manager": {
        "description": "Manages multiple engineering teams and drives technical strategy. Balances people management with technical leadership, sets engineering standards, and aligns team output with business goals.",
        "required_skills": ["Team Leadership", "Software Architecture", "Agile", "Hiring", "Strategic Planning", "Stakeholder Management"],
        "preferred_skills": ["Technical Mentoring", "Budgeting", "Cross-Functional Leadership", "Performance Management", "OKRs"],
    },
    "Senior Frontend Developer": {
        "description": "Leads frontend development of complex web applications. Makes UI architecture decisions, ensures performance and accessibility, and mentors junior developers.",
        "required_skills": ["JavaScript", "TypeScript", "React", "HTML", "CSS", "Git", "Performance Optimization"],
        "preferred_skills": ["Next.js", "Testing", "Design Systems", "Accessibility", "State Management"],
    },
    "Senior Full-Stack Developer": {
        "description": "Leads end-to-end development of web applications across frontend and backend. Makes architecture decisions, mentors developers, and delivers complex features independently.",
        "required_skills": ["JavaScript", "TypeScript", "React", "Node.js", "SQL", "System Design", "Git"],
        "preferred_skills": ["Docker", "Cloud Platforms", "GraphQL", "CI/CD", "Microservices"],
    },
    "Senior Mobile Developer": {
        "description": "Leads mobile application development for iOS and/or Android platforms. Makes architectural decisions, optimizes app performance, and mentors junior mobile developers.",
        "required_skills": ["React Native", "Mobile Development", "JavaScript", "REST APIs", "Git", "App Store Deployment"],
        "preferred_skills": ["Swift", "Kotlin", "Flutter", "Performance Optimization", "CI/CD"],
    },
    "Senior Network Engineer": {
        "description": "Designs and manages complex enterprise network infrastructure. Leads network architecture decisions, troubleshoots critical issues, and ensures network security and performance.",
        "required_skills": ["Network Architecture", "Routing & Switching", "Firewall Management", "Network Security", "Troubleshooting", "TCP/IP"],
        "preferred_skills": ["Cisco", "Cloud Networking", "SD-WAN", "Network Automation", "Monitoring"],
    },
    "Senior QA Engineer": {
        "description": "Leads quality assurance strategy and test architecture. Designs test frameworks, drives automation adoption, and ensures comprehensive test coverage across the product.",
        "required_skills": ["Test Automation", "Test Strategy", "Selenium", "Python", "CI/CD", "Performance Testing"],
        "preferred_skills": ["Cypress", "API Testing", "Load Testing", "Security Testing", "Mentoring"],
    },
    "Senior Software Developer": {
        "description": "Leads software development of complex features and systems. Makes design decisions, writes high-quality code, conducts code reviews, and mentors junior developers.",
        "required_skills": ["Python", "Java", "SQL", "System Design", "Git", "Code Review"],
        "preferred_skills": ["Docker", "Cloud Platforms", "Microservices", "CI/CD", "Technical Documentation"],
    },
    "Software Developer": {
        "description": "Designs, develops, and maintains software applications. Writes clean code, participates in code reviews, and collaborates with teams to deliver reliable software solutions.",
        "required_skills": ["Python", "Java", "SQL", "Git", "REST APIs"],
        "preferred_skills": ["Docker", "Cloud Platforms", "Testing", "Agile", "CI/CD"],
    },
    "Solutions Architect": {
        "description": "Designs end-to-end technical solutions that meet business requirements. Evaluates technologies, creates architecture blueprints, and guides development teams through implementation.",
        "required_skills": ["Solution Architecture", "Cloud Architecture", "API Design", "Requirements Analysis", "Technical Documentation", "Stakeholder Management"],
        "preferred_skills": ["AWS", "Microservices", "Security Architecture", "Pre-Sales", "Cost Optimization"],
    },
    "Staff Engineer": {
        "description": "Provides deep technical leadership across multiple teams and projects. Solves the hardest engineering problems, defines technical strategy, and raises the engineering bar organization-wide.",
        "required_skills": ["System Design", "Software Architecture", "Technical Leadership", "Code Review", "Cross-Team Collaboration", "Performance Optimization"],
        "preferred_skills": ["Distributed Systems", "Mentoring", "Technical Writing", "Open Source", "Strategic Planning"],
    },
    "Technical Lead": {
        "description": "Leads a development team technically, making architecture and design decisions. Balances hands-on coding with mentoring, code reviews, and technical planning.",
        "required_skills": ["Software Architecture", "Team Leadership", "Code Review", "System Design", "Agile", "Git"],
        "preferred_skills": ["CI/CD", "Cloud Platforms", "Mentoring", "Technical Documentation", "DevOps"],
    },
    "Technical Writer": {
        "description": "Creates clear, accurate technical documentation including API docs, user guides, and knowledge bases. Collaborates with engineers to make complex technical concepts accessible.",
        "required_skills": ["Technical Writing", "Documentation", "Communication", "Markdown", "Content Organization"],
        "preferred_skills": ["API Documentation", "Git", "HTML", "Swagger", "Information Architecture"],
    },

    # ── Finance ───────────────────────────────────────
    "Account Executive": {
        "description": "Manages client accounts and drives revenue growth through relationship building and strategic selling. Identifies new business opportunities and ensures client satisfaction and retention.",
        "required_skills": ["Sales", "Client Relationship Management", "Negotiation", "Communication", "CRM Software"],
        "preferred_skills": ["Salesforce", "Pipeline Management", "Presentation", "Contract Negotiation", "Business Development"],
    },
    "Account Manager": {
        "description": "Oversees a portfolio of client accounts, ensuring long-term satisfaction and revenue growth. Develops account strategies, manages renewals, and identifies upsell opportunities.",
        "required_skills": ["Account Management", "Client Relationship Management", "Strategic Planning", "Communication", "Revenue Growth"],
        "preferred_skills": ["Salesforce", "Contract Negotiation", "Cross-Selling", "Budgeting", "Team Leadership"],
    },
    "Accountant": {
        "description": "Prepares and maintains financial records, ensures compliance with accounting standards, and produces financial reports. Handles journal entries, reconciliations, and tax filings.",
        "required_skills": ["Financial Accounting", "Bookkeeping", "Tax Compliance", "Excel", "Financial Reporting"],
        "preferred_skills": ["SAP", "QuickBooks", "Audit", "BIR Compliance", "ERP Systems"],
    },
    "Accounting Clerk": {
        "description": "Performs routine accounting tasks including data entry, invoice processing, and bank reconciliations. Supports the accounting team with accurate record-keeping.",
        "required_skills": ["Bookkeeping", "Data Entry", "Excel", "Accounts Payable/Receivable", "Attention to Detail"],
        "preferred_skills": ["QuickBooks", "SAP", "Filing", "Basic Accounting", "Communication"],
    },
    "Accounting Manager": {
        "description": "Manages the accounting department and oversees financial reporting, month-end close, and compliance. Leads accounting staff and ensures accuracy of financial statements.",
        "required_skills": ["Financial Reporting", "Team Leadership", "GAAP/IFRS", "Tax Compliance", "Month-End Close", "Budgeting"],
        "preferred_skills": ["SAP", "ERP Systems", "Audit Management", "Process Improvement", "Stakeholder Management"],
    },
    "Auditor": {
        "description": "Examines financial records and internal controls to ensure accuracy and regulatory compliance. Conducts audits, identifies risks, and recommends improvements to business processes.",
        "required_skills": ["Auditing", "Financial Analysis", "Risk Assessment", "Compliance", "Communication"],
        "preferred_skills": ["Internal Controls", "SOX Compliance", "Data Analytics", "SAP", "Report Writing"],
    },
    "CFO": {
        "description": "Leads the finance organization and sets financial strategy. Oversees financial planning, capital allocation, investor relations, and ensures the company's long-term financial health.",
        "required_skills": ["Financial Strategy", "Financial Planning & Analysis", "Team Leadership", "Budgeting", "Stakeholder Management", "Risk Management"],
        "preferred_skills": ["Fundraising", "M&A", "Board Communication", "Regulatory Compliance", "ERP Systems"],
    },
    "FP&A Manager": {
        "description": "Leads financial planning and analysis, building forecasts, budgets, and financial models. Provides strategic financial insights to leadership for data-driven decision-making.",
        "required_skills": ["Financial Modeling", "Budgeting", "Forecasting", "Excel", "Financial Analysis", "Presentation"],
        "preferred_skills": ["Power BI", "SAP", "Scenario Analysis", "Team Leadership", "SQL"],
    },
    "Finance Manager": {
        "description": "Oversees financial operations including budgeting, reporting, and cash flow management. Manages the finance team and provides financial guidance to business leaders.",
        "required_skills": ["Financial Management", "Budgeting", "Financial Reporting", "Team Leadership", "Cash Flow Management"],
        "preferred_skills": ["SAP", "ERP Systems", "Financial Modeling", "Audit", "Process Improvement"],
    },
    "Investment Analyst": {
        "description": "Researches and analyzes investment opportunities including stocks, bonds, and alternative assets. Builds financial models, prepares investment recommendations, and monitors portfolio performance.",
        "required_skills": ["Financial Analysis", "Financial Modeling", "Excel", "Valuation", "Research"],
        "preferred_skills": ["Bloomberg", "Python", "SQL", "Portfolio Management", "Industry Research"],
    },
    "Junior Accountant": {
        "description": "Assists in preparing financial records and reports under senior guidance. Handles data entry, reconciliations, and basic bookkeeping while learning accounting principles.",
        "required_skills": ["Bookkeeping", "Excel", "Data Entry", "Basic Accounting", "Attention to Detail"],
        "preferred_skills": ["QuickBooks", "Tax Basics", "Financial Reporting", "Communication"],
    },
    "Payroll Specialist": {
        "description": "Processes employee payroll, ensures accurate compensation, and manages payroll taxes and deductions. Maintains payroll records and ensures compliance with labor regulations.",
        "required_skills": ["Payroll Processing", "Tax Compliance", "Excel", "Labor Law", "Attention to Detail"],
        "preferred_skills": ["HRIS", "SAP", "Benefits Administration", "Communication", "Data Entry"],
    },
    "Senior Auditor": {
        "description": "Leads audit engagements and supervises audit teams. Plans and executes complex audits, evaluates internal controls, and presents findings to management with actionable recommendations.",
        "required_skills": ["Auditing", "Financial Analysis", "Risk Assessment", "Team Leadership", "Compliance", "Report Writing"],
        "preferred_skills": ["Internal Controls", "SOX Compliance", "Data Analytics", "SAP", "CPA"],
    },
    "Senior Financial Analyst": {
        "description": "Leads financial analysis and modeling for strategic initiatives. Builds complex financial models, prepares executive presentations, and provides insights that drive business decisions.",
        "required_skills": ["Financial Modeling", "Financial Analysis", "Excel", "Forecasting", "Presentation", "SQL"],
        "preferred_skills": ["Power BI", "Python", "SAP", "Scenario Analysis", "Valuation"],
    },
    "Tax Accountant": {
        "description": "Prepares and files tax returns, ensures compliance with Philippine tax regulations, and minimizes tax liability. Handles BIR filings, tax planning, and audit support.",
        "required_skills": ["Tax Compliance", "Tax Preparation", "BIR Regulations", "Excel", "Financial Reporting"],
        "preferred_skills": ["SAP", "Tax Planning", "Transfer Pricing", "Audit Support", "ERP Systems"],
    },
    "Tax Manager": {
        "description": "Leads the tax function and ensures organization-wide tax compliance. Manages tax planning strategies, oversees tax filings, and represents the company in tax audits and regulatory matters.",
        "required_skills": ["Tax Compliance", "Tax Planning", "Team Leadership", "BIR Regulations", "Financial Reporting", "Risk Management"],
        "preferred_skills": ["Transfer Pricing", "International Tax", "ERP Systems", "SAP", "Audit Management"],
    },
    "Tax Tech Consultant": {
        "description": "Combines tax expertise with technology to automate tax processes and implement tax software solutions. Advises on digital tax transformation and tax technology strategy.",
        "required_skills": ["Tax Compliance", "Tax Software", "Process Automation", "Requirements Analysis", "Implementation"],
        "preferred_skills": ["SAP", "ERP Systems", "Data Analytics", "Python", "Change Management"],
    },
    "VP of Finance": {
        "description": "Oversees all financial operations and strategy as a senior executive. Directs financial planning, treasury, accounting, and ensures financial sustainability and regulatory compliance.",
        "required_skills": ["Financial Strategy", "Team Leadership", "Financial Planning & Analysis", "Budgeting", "Stakeholder Management", "Risk Management"],
        "preferred_skills": ["Board Communication", "M&A", "Capital Markets", "ERP Systems", "Regulatory Compliance"],
    },

    # ── HR ────────────────────────────────────────────
    "Administrative Assistant": {
        "description": "Provides administrative support including scheduling, correspondence, file management, and office coordination. Ensures smooth daily operations and supports team productivity.",
        "required_skills": ["Microsoft Office", "Communication", "Organization", "Scheduling", "Data Entry"],
        "preferred_skills": ["Google Workspace", "Calendar Management", "Filing", "Travel Coordination", "Customer Service"],
    },
    "Executive Assistant": {
        "description": "Provides high-level administrative support to senior executives. Manages complex calendars, coordinates meetings, prepares reports, and handles confidential information with discretion.",
        "required_skills": ["Calendar Management", "Communication", "Microsoft Office", "Organization", "Confidentiality"],
        "preferred_skills": ["Travel Coordination", "Presentation Preparation", "Meeting Minutes", "Project Coordination", "Google Workspace"],
    },
    "HR Coordinator": {
        "description": "Supports HR operations including recruitment coordination, onboarding, benefits administration, and employee records management. Serves as the first point of contact for HR inquiries.",
        "required_skills": ["HR Operations", "Recruitment Coordination", "Communication", "HRIS", "Onboarding"],
        "preferred_skills": ["Benefits Administration", "Labor Law", "Excel", "Employee Relations", "Training Coordination"],
    },
    "HR Director": {
        "description": "Leads the HR function and develops people strategies aligned with business objectives. Oversees talent acquisition, employee engagement, compensation, and organizational development.",
        "required_skills": ["HR Strategy", "Team Leadership", "Talent Management", "Labor Law", "Organizational Development", "Stakeholder Management"],
        "preferred_skills": ["Change Management", "Executive Coaching", "Compensation Design", "HRIS", "Board Communication"],
    },
    "HR Manager": {
        "description": "Manages HR operations and leads the HR team. Oversees recruitment, employee relations, performance management, and ensures compliance with labor laws and company policies.",
        "required_skills": ["HR Management", "Recruitment", "Employee Relations", "Labor Law", "Performance Management", "Team Leadership"],
        "preferred_skills": ["HRIS", "Training & Development", "Compensation & Benefits", "Conflict Resolution", "Change Management"],
    },
    "HR Specialist": {
        "description": "Handles specialized HR functions such as recruitment, benefits administration, or employee relations. Implements HR policies and provides guidance to employees and managers.",
        "required_skills": ["Recruitment", "Employee Relations", "HRIS", "Labor Law", "Communication"],
        "preferred_skills": ["Benefits Administration", "Performance Management", "Training", "Excel", "Conflict Resolution"],
    },

    # ── IT ────────────────────────────────────────────
    "IT Project Manager": {
        "description": "Manages IT projects from initiation through delivery. Coordinates cross-functional teams, manages budgets and timelines, and ensures projects meet business requirements and quality standards.",
        "required_skills": ["Project Management", "Agile", "Stakeholder Management", "Risk Management", "Budgeting", "Communication"],
        "preferred_skills": ["Jira", "Scrum", "ITIL", "Vendor Management", "PMP"],
    },
    "IT Service Manager": {
        "description": "Manages IT service delivery and ensures IT services meet business needs. Oversees incident management, service level agreements, and continuous service improvement.",
        "required_skills": ["ITIL", "Service Management", "Incident Management", "Team Leadership", "Stakeholder Management", "SLA Management"],
        "preferred_skills": ["ServiceNow", "Change Management", "Problem Management", "Vendor Management", "Budgeting"],
    },

    # ── Legal / Compliance ────────────────────────────
    "Compliance Officer": {
        "description": "Ensures organizational compliance with laws, regulations, and internal policies. Develops compliance programs, conducts risk assessments, and provides regulatory guidance.",
        "required_skills": ["Regulatory Compliance", "Risk Assessment", "Policy Development", "Communication", "Auditing"],
        "preferred_skills": ["Data Privacy", "Anti-Money Laundering", "Training", "Report Writing", "Internal Controls"],
    },

    # ── Management ────────────────────────────────────
    "BPO Operations Manager": {
        "description": "Manages BPO operations including service delivery, team performance, and client satisfaction. Drives operational efficiency, manages SLAs, and leads process improvement initiatives.",
        "required_skills": ["Operations Management", "Team Leadership", "SLA Management", "Process Improvement", "Client Management", "KPI Management"],
        "preferred_skills": ["Six Sigma", "Workforce Management", "Budgeting", "Lean", "Quality Assurance"],
    },
    "BPO Team Leader": {
        "description": "Leads a BPO team to meet performance targets and service quality standards. Coaches agents, monitors KPIs, handles escalations, and drives team engagement.",
        "required_skills": ["Team Leadership", "Performance Management", "Coaching", "KPI Management", "Communication", "Escalation Management"],
        "preferred_skills": ["Workforce Management", "Quality Monitoring", "Training", "CRM Software", "Reporting"],
    },
    "CHRO": {
        "description": "Leads the entire human resources function as a C-suite executive. Sets people strategy, drives culture, oversees talent acquisition and development, and ensures HR supports business growth.",
        "required_skills": ["HR Strategy", "Executive Leadership", "Organizational Development", "Talent Management", "Stakeholder Management", "Change Management"],
        "preferred_skills": ["Board Communication", "M&A HR", "Compensation Design", "Employer Branding", "Cultural Transformation"],
    },
    "CMO": {
        "description": "Leads the marketing organization and sets brand and growth strategy. Oversees all marketing channels, brand positioning, demand generation, and marketing technology investments.",
        "required_skills": ["Marketing Strategy", "Brand Management", "Team Leadership", "Digital Marketing", "Stakeholder Management", "Budgeting"],
        "preferred_skills": ["Growth Marketing", "Data-Driven Marketing", "Product Marketing", "Executive Communication", "Vendor Management"],
    },
    "Customer Success Manager": {
        "description": "Ensures customers achieve their desired outcomes using the company's products. Builds relationships, drives adoption, reduces churn, and identifies expansion opportunities.",
        "required_skills": ["Customer Success", "Client Relationship Management", "Communication", "Data Analysis", "Onboarding"],
        "preferred_skills": ["CRM Software", "Product Knowledge", "Upselling", "Presentation", "Project Management"],
    },
    "FinTech Operations Manager": {
        "description": "Manages operations for a financial technology company including payment processing, compliance, and customer operations. Ensures operational efficiency and regulatory compliance.",
        "required_skills": ["Operations Management", "FinTech", "Compliance", "Team Leadership", "Process Improvement", "Risk Management"],
        "preferred_skills": ["Payment Systems", "Anti-Money Laundering", "Data Analytics", "Vendor Management", "Automation"],
    },
    "Junior Project Manager": {
        "description": "Assists in managing projects under senior guidance. Coordinates tasks, tracks progress, communicates with stakeholders, and learns project management methodologies.",
        "required_skills": ["Project Coordination", "Communication", "Excel", "Scheduling", "Documentation"],
        "preferred_skills": ["Jira", "Agile", "Risk Management", "Presentation", "Time Management"],
    },
    "Marketing Manager": {
        "description": "Plans and executes marketing campaigns to drive brand awareness and lead generation. Manages marketing budgets, coordinates teams, and measures campaign performance.",
        "required_skills": ["Marketing Strategy", "Campaign Management", "Team Leadership", "Budgeting", "Communication", "Analytics"],
        "preferred_skills": ["Digital Marketing", "Content Strategy", "SEO/SEM", "CRM Software", "Social Media"],
    },
    "Office Manager": {
        "description": "Manages daily office operations including facilities, supplies, and administrative staff. Ensures a productive work environment and handles vendor relationships and office budgets.",
        "required_skills": ["Office Administration", "Team Leadership", "Budgeting", "Vendor Management", "Communication", "Organization"],
        "preferred_skills": ["Facilities Management", "Event Planning", "HRIS", "Procurement", "Microsoft Office"],
    },
    "Operations Director": {
        "description": "Directs company-wide operations including process optimization, supply chain, and operational strategy. Drives efficiency, scalability, and alignment with business objectives.",
        "required_skills": ["Operations Management", "Strategic Planning", "Team Leadership", "Process Improvement", "Budgeting", "Stakeholder Management"],
        "preferred_skills": ["Lean", "Six Sigma", "Supply Chain", "Vendor Management", "Change Management"],
    },
    "Project Manager": {
        "description": "Manages projects from initiation to completion, coordinating cross-functional teams to deliver on time and within budget. Handles scope, risk, and stakeholder communication.",
        "required_skills": ["Project Management", "Stakeholder Management", "Risk Management", "Budgeting", "Communication", "Agile"],
        "preferred_skills": ["Jira", "Scrum", "PMP", "Vendor Management", "Change Management"],
    },
    "QA Manager": {
        "description": "Leads the quality assurance team and defines testing strategy. Oversees test planning, automation initiatives, and quality metrics to ensure product reliability and customer satisfaction.",
        "required_skills": ["QA Strategy", "Test Management", "Team Leadership", "Test Automation", "Quality Metrics", "Agile"],
        "preferred_skills": ["CI/CD", "Performance Testing", "Security Testing", "Jira", "Budgeting"],
    },
    "Sales Manager": {
        "description": "Leads and motivates a sales team to meet revenue targets. Develops sales strategies, manages pipelines, coaches representatives, and builds relationships with key accounts.",
        "required_skills": ["Sales Strategy", "Team Leadership", "Pipeline Management", "Negotiation", "Communication", "CRM Software"],
        "preferred_skills": ["Salesforce", "Revenue Forecasting", "Key Account Management", "Coaching", "Market Analysis"],
    },
    "Senior Project Manager": {
        "description": "Leads complex, high-impact projects and programs. Manages large budgets, coordinates multiple workstreams, and provides strategic project leadership to achieve business outcomes.",
        "required_skills": ["Project Management", "Stakeholder Management", "Risk Management", "Budgeting", "Team Leadership", "Strategic Planning"],
        "preferred_skills": ["Program Management", "PMP", "Agile", "Vendor Management", "Change Management"],
    },

    # ── Marketing ─────────────────────────────────────
    "Digital Marketing Specialist": {
        "description": "Plans and executes digital marketing campaigns across channels including social media, email, SEO, and paid advertising. Analyzes campaign performance and optimizes for ROI.",
        "required_skills": ["Digital Marketing", "SEO/SEM", "Social Media Marketing", "Google Analytics", "Content Marketing"],
        "preferred_skills": ["Google Ads", "Facebook Ads", "Email Marketing", "Copywriting", "A/B Testing"],
    },
    "Director of Marketing": {
        "description": "Directs the marketing department and sets marketing strategy. Oversees brand, demand generation, content, and digital marketing while managing budgets and team performance.",
        "required_skills": ["Marketing Strategy", "Team Leadership", "Brand Management", "Budgeting", "Digital Marketing", "Stakeholder Management"],
        "preferred_skills": ["Growth Marketing", "Product Marketing", "Analytics", "Content Strategy", "Executive Communication"],
    },
    "Marketing Analyst": {
        "description": "Analyzes marketing data to measure campaign effectiveness and identify growth opportunities. Builds dashboards, generates insights, and supports data-driven marketing decisions.",
        "required_skills": ["Data Analysis", "Google Analytics", "Excel", "Marketing Metrics", "Reporting"],
        "preferred_skills": ["SQL", "Power BI", "A/B Testing", "Python", "Attribution Modeling"],
    },
    "Marketing Coordinator": {
        "description": "Supports marketing campaigns by coordinating logistics, managing content calendars, and assisting with event planning. Handles administrative marketing tasks and tracks campaign progress.",
        "required_skills": ["Marketing Coordination", "Communication", "Social Media", "Content Management", "Organization"],
        "preferred_skills": ["Canva", "Email Marketing", "Event Planning", "Copywriting", "Google Analytics"],
    },

    # ── Product ───────────────────────────────────────
    "Agile Coach": {
        "description": "Guides teams and organizations in adopting and improving agile practices. Facilitates ceremonies, coaches team members, and helps remove impediments to agile transformation.",
        "required_skills": ["Agile", "Scrum", "Coaching", "Facilitation", "Team Dynamics", "Change Management"],
        "preferred_skills": ["Kanban", "SAFe", "Lean", "Conflict Resolution", "Training"],
    },
    "Business Analyst": {
        "description": "Bridges business needs and technical solutions by gathering requirements, analyzing processes, and defining specifications. Creates documentation and ensures solutions meet stakeholder expectations.",
        "required_skills": ["Requirements Analysis", "Business Process Mapping", "Documentation", "Communication", "SQL"],
        "preferred_skills": ["Jira", "Wireframing", "Data Analysis", "Agile", "User Stories"],
    },
    "CPO": {
        "description": "Leads the product organization as a C-suite executive. Sets product vision and strategy, aligns product roadmap with business goals, and drives product-led growth.",
        "required_skills": ["Product Strategy", "Team Leadership", "Strategic Planning", "Stakeholder Management", "User Research", "Roadmap Planning"],
        "preferred_skills": ["Data-Driven Decision Making", "Go-to-Market", "Board Communication", "P&L Management", "Product-Led Growth"],
    },
    "Director of Product": {
        "description": "Directs multiple product teams and sets product strategy for a product line or business unit. Aligns product roadmaps with company vision and manages product team performance.",
        "required_skills": ["Product Strategy", "Team Leadership", "Roadmap Planning", "Stakeholder Management", "Data Analysis", "User Research"],
        "preferred_skills": ["A/B Testing", "Product Analytics", "Go-to-Market", "Cross-Functional Leadership", "Budgeting"],
    },
    "FinTech Product Manager": {
        "description": "Manages fintech products including digital payments, lending platforms, or investment tools. Balances user needs, regulatory compliance, and business goals in the financial technology space.",
        "required_skills": ["Product Management", "FinTech", "Roadmap Planning", "User Research", "Stakeholder Management", "Compliance"],
        "preferred_skills": ["Payment Systems", "Data Analysis", "Agile", "Regulatory Knowledge", "A/B Testing"],
    },
    "Junior Product Manager": {
        "description": "Assists in product management under senior guidance. Helps with user research, feature specifications, backlog grooming, and stakeholder communication while learning product craft.",
        "required_skills": ["Product Thinking", "Communication", "User Research", "Documentation", "Agile"],
        "preferred_skills": ["Jira", "Data Analysis", "Wireframing", "SQL", "A/B Testing"],
    },
    "Product Analyst": {
        "description": "Analyzes product usage data to generate insights that drive product decisions. Tracks key metrics, runs A/B tests, and helps product teams understand user behavior.",
        "required_skills": ["Data Analysis", "SQL", "Product Metrics", "A/B Testing", "Communication"],
        "preferred_skills": ["Python", "Amplitude", "Mixpanel", "Excel", "Data Visualization"],
    },
    "Program Manager": {
        "description": "Manages large-scale programs consisting of multiple related projects. Coordinates cross-functional teams, manages dependencies, and ensures programs deliver strategic business outcomes.",
        "required_skills": ["Program Management", "Stakeholder Management", "Risk Management", "Communication", "Strategic Planning", "Budgeting"],
        "preferred_skills": ["Agile", "PMP", "Change Management", "Vendor Management", "OKRs"],
    },
    "VP of Product": {
        "description": "Oversees the product function at the executive level. Defines product vision, aligns product strategy with company goals, and leads product leaders across the organization.",
        "required_skills": ["Product Strategy", "Executive Leadership", "Strategic Planning", "Stakeholder Management", "Team Leadership", "Roadmap Planning"],
        "preferred_skills": ["Data-Driven Decision Making", "Go-to-Market", "Board Communication", "Product-Led Growth", "M&A"],
    },

    # ── Sales ─────────────────────────────────────────
    "Director of Sales": {
        "description": "Directs the sales organization and sets revenue strategy. Builds and manages sales teams, sets quotas, develops sales processes, and drives revenue growth across the company.",
        "required_skills": ["Sales Strategy", "Team Leadership", "Revenue Forecasting", "Pipeline Management", "Stakeholder Management", "Negotiation"],
        "preferred_skills": ["Salesforce", "Key Account Management", "Sales Operations", "Market Analysis", "Board Communication"],
    },
    "Sales Representative": {
        "description": "Identifies and pursues sales opportunities through prospecting, demos, and relationship building. Manages the full sales cycle from lead generation to closing deals.",
        "required_skills": ["Sales", "Communication", "Negotiation", "CRM Software", "Prospecting"],
        "preferred_skills": ["Salesforce", "Cold Calling", "Presentation", "Pipeline Management", "Product Knowledge"],
    },

    # ── Security ──────────────────────────────────────
    "CISO": {
        "description": "Leads the organization's information security strategy as a C-suite executive. Oversees security operations, compliance, risk management, and incident response across the enterprise.",
        "required_skills": ["Information Security Strategy", "Risk Management", "Compliance", "Team Leadership", "Incident Response", "Stakeholder Management"],
        "preferred_skills": ["Security Architecture", "Board Communication", "Budgeting", "Regulatory Compliance", "Vendor Management"],
    },
    "Cybersecurity Analyst": {
        "description": "Monitors and protects systems from cyber threats. Analyzes security alerts, investigates incidents, maintains security tools, and helps implement security policies.",
        "required_skills": ["Security Monitoring", "Incident Response", "SIEM", "Vulnerability Assessment", "Network Security"],
        "preferred_skills": ["Firewall Management", "IDS/IPS", "Python", "Forensics", "Compliance"],
    },
    "Junior Cybersecurity Analyst": {
        "description": "Supports the security team by monitoring alerts, triaging incidents, and maintaining security documentation. Learns cybersecurity tools and practices under senior guidance.",
        "required_skills": ["Security Monitoring", "Incident Triage", "Network Basics", "Communication"],
        "preferred_skills": ["SIEM", "Vulnerability Scanning", "Linux", "Firewall Basics", "Compliance"],
    },
    "Penetration Tester": {
        "description": "Conducts authorized security testing to identify vulnerabilities in systems, networks, and applications. Simulates attacks, documents findings, and provides remediation recommendations.",
        "required_skills": ["Penetration Testing", "Vulnerability Assessment", "Network Security", "Web Application Security", "Report Writing"],
        "preferred_skills": ["Burp Suite", "Metasploit", "Python", "OWASP", "Cloud Security"],
    },
    "Security Architect": {
        "description": "Designs and implements enterprise security architecture. Defines security standards, evaluates technologies, and ensures systems are built with security by design.",
        "required_skills": ["Security Architecture", "Network Security", "Cloud Security", "Risk Assessment", "Identity & Access Management", "Compliance"],
        "preferred_skills": ["Zero Trust", "SIEM", "Encryption", "Threat Modeling", "Vendor Evaluation"],
    },
    "Security Consultant": {
        "description": "Advises organizations on security strategy and helps implement security solutions. Conducts security assessments, develops security policies, and provides expert guidance on risk mitigation.",
        "required_skills": ["Security Assessment", "Risk Management", "Compliance", "Security Architecture", "Communication", "Report Writing"],
        "preferred_skills": ["Penetration Testing", "Cloud Security", "ISO 27001", "Policy Development", "Training"],
    },

    # ── Missing roles (found after first run) ─────────
    "Junior Data Analyst": {
        "description": "Assists in analyzing data and generating reports under senior guidance. Cleans datasets, creates basic visualizations, and supports the analytics team with ad-hoc queries.",
        "required_skills": ["Excel", "SQL", "Data Analysis", "Communication"],
        "preferred_skills": ["Python", "Power BI", "Tableau", "Statistics", "Google Sheets"],
    },
    "Junior UI/UX Designer": {
        "description": "Supports the design team by creating wireframes, mockups, and prototypes. Assists with user research, design system maintenance, and visual design under senior guidance.",
        "required_skills": ["Figma", "UI Design", "Wireframing", "Communication"],
        "preferred_skills": ["User Research", "Prototyping", "Adobe Creative Suite", "Design Systems", "Accessibility"],
    },
    "Lead Data Scientist": {
        "description": "Leads a team of data scientists and drives the data science roadmap. Oversees model development, sets best practices, and ensures data science projects deliver measurable business value.",
        "required_skills": ["Machine Learning", "Python", "Statistical Modeling", "Team Leadership", "SQL", "Stakeholder Management"],
        "preferred_skills": ["Deep Learning", "MLOps", "A/B Testing", "Mentoring", "Cloud Platforms"],
    },
    "Mobile Engineering Lead": {
        "description": "Leads a mobile engineering team and sets technical direction for mobile apps. Makes architecture decisions, ensures code quality, and drives mobile platform best practices.",
        "required_skills": ["Mobile Development", "React Native", "Team Leadership", "System Design", "Code Review", "Git"],
        "preferred_skills": ["Swift", "Kotlin", "Flutter", "CI/CD", "Performance Optimization"],
    },
    "Principal Engineer": {
        "description": "Provides the highest level of individual technical contribution across the engineering organization. Tackles the most complex problems, defines technical vision, and influences company-wide engineering decisions.",
        "required_skills": ["System Design", "Software Architecture", "Technical Leadership", "Cross-Team Collaboration", "Performance Optimization", "Technical Strategy"],
        "preferred_skills": ["Distributed Systems", "Mentoring", "Technical Writing", "Open Source", "Industry Thought Leadership"],
    },
    "Senior Business Analyst": {
        "description": "Leads business analysis for complex projects and initiatives. Defines requirements, models business processes, and ensures solutions align with strategic objectives. Mentors junior analysts.",
        "required_skills": ["Requirements Analysis", "Business Process Mapping", "Stakeholder Management", "Documentation", "SQL", "Data Analysis"],
        "preferred_skills": ["Jira", "Wireframing", "Agile", "User Stories", "Change Management"],
    },
    "Technical Support Specialist": {
        "description": "Provides technical assistance to customers and internal users. Troubleshoots hardware and software issues, manages support tickets, and documents solutions for knowledge bases.",
        "required_skills": ["Troubleshooting", "Communication", "Ticketing Systems", "Customer Service", "Technical Documentation"],
        "preferred_skills": ["Networking Basics", "Active Directory", "Remote Support", "Linux", "ITIL"],
    },
}


def main():
    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    enriched = 0
    skipped_titles = []

    for role in data["roles"]:
        # Only enrich roles that have empty required_skills
        if role.get("required_skills"):
            continue

        title = role["title"]
        info = ENRICHMENT.get(title)

        if not info:
            skipped_titles.append(title)
            continue

        role["required_skills"] = info["required_skills"]
        role["preferred_skills"] = info["preferred_skills"]
        role["description"] = info["description"]
        enriched += 1

    with open(ROLES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Enriched {enriched} roles")
    if skipped_titles:
        print(f"Skipped {len(skipped_titles)} (no mapping):")
        for t in sorted(skipped_titles):
            print(f"  - {t}")


if __name__ == "__main__":
    main()
