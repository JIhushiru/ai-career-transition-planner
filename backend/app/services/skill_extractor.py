import json
import re
from pathlib import Path

import spacy
from spacy.language import Language


class SkillExtractor:
    TECH_PATTERNS: dict[str, str] = {
        "technical": (
            r"\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Ruby|PHP|Swift|Kotlin"
            r"|Scala|(?<![A-Z])R(?![\.\w])|MATLAB|SQL|HTML|CSS|Sass|LESS|Perl|Lua|Dart|Elixir|Haskell"
            r"|Shell|Bash|PowerShell|VBA|ABAP|COBOL|Fortran|Solidity|Markdown|ARM"
            r"|Statistics|OOP|Data\s*Structures|Algorithms|Linux"
            r"|Visual\s*Basic)\b"
        ),
        "framework": (
            r"\b(React|React\s*Native|Angular|Vue\.?js|Next\.?js|Nuxt\.?js|Svelte|Django|Flask|FastAPI"
            r"|Spring\s*Boot|\.NET|ASP\.NET|Node\.?js|Express\.?js|NestJS|Rails"
            r"|Laravel|Symfony|TensorFlow|PyTorch|Keras|Scikit-learn|Pandas|NumPy"
            r"|Matplotlib|Seaborn|Plotly|Streamlit|Gradio|LangChain|Tailwind\s*CSS"
            r"|Robot\s*Framework|Cypress|Playwright|Selenium|Unity)\b"
        ),
        "tool": (
            r"\b(Docker|Kubernetes|Git|GitHub|GitLab|Bitbucket|AWS|Azure|GCP"
            r"|Jenkins|CircleCI|Travis\s*CI|Terraform|Ansible|Puppet|Chef"
            r"|Figma|Sketch|Adobe\s*XD|Photoshop|Illustrator|Canva"
            r"|Tableau|Power\s*BI|Looker|Metabase|Grafana|Datadog"
            r"|Jira|Confluence|Slack|Trello|Notion|Asana"
            r"|Postman|Swagger|Nginx|Apache|Redis|RabbitMQ|Kafka"
            r"|MongoDB|PostgreSQL|MySQL|SQLite|Oracle|DynamoDB|Cassandra"
            r"|Elasticsearch|Supabase|Firebase|Vercel|Netlify|Heroku"
            r"|SAP|QuickBooks|Xero|Sage|Tally|Zoho|Snowflake|BigQuery"
            r"|Airflow|Spark|dbt|Excel|HRIS|Active\s*Directory|SIEM"
            r"|Ahrefs|SEMrush|Hubspot|Salesforce|Miro|WordPress"
            r"|MS\s*Office|OneSource|Sherlock\s*System)\b"
        ),
        "soft": (
            r"\b(leadership|communication|teamwork|team\s*work|problem[- ]solving"
            r"|critical\s*thinking|project\s*management|time\s*management"
            r"|adaptability|creativity|collaboration|mentoring|coaching"
            r"|presentation|negotiation|conflict\s*resolution"
            r"|strategic\s*planning|decision[- ]making|analytical\s*thinking"
            r"|team\s*leadership|stakeholder\s*management|change\s*management"
            r"|vendor\s*management|team\s*management|client\s*management"
            r"|public\s*speaking|technical\s*writing)\b"
        ),
        "domain": (
            r"\b(machine\s*learning|deep\s*learning|natural\s*language\s*processing|NLP"
            r"|computer\s*vision|data\s*science|data\s*engineering|data\s*analytics"
            r"|business\s*intelligence|DevOps|MLOps|CI/CD|microservices"
            r"|REST\s*APIs?|GraphQL|web\s*scraping|ETL|data\s*warehousing"
            r"|agile|scrum|kanban|lean|six\s*sigma"
            r"|financial\s*analysis|tax\s*compliance|auditing|bookkeeping"
            r"|accounting|budgeting|forecasting|financial\s*reporting"
            r"|BPO|customer\s*service|quality\s*assurance|QA|testing"
            r"|cloud\s*architecture|system\s*design|data\s*analysis"
            r"|A/B\s*testing|risk\s*management|process\s*improvement"
            r"|compliance|user\s*research|data\s*governance|SEO|SEM"
            r"|digital\s*marketing|network\s*security|cloud\s*security"
            r"|incident\s*response|data\s*modeling|data\s*visualization"
            r"|infrastructure\s*as\s*code|accessibility|cybersecurity"
            r"|GAAP|IFRS|VAT|GST|WHT|SUT"
            r"|indirect\s*tax(?:es)?|withholding\s*tax"
            r"|accounts\s*payable|vendor\s*master\s*data|supplier\s*master\s*data"
            r"|ERP|invoice\s*processing|regulatory\s*compliance"
            r"|process\s*standardization|process\s*optimization"
            r"|tax\s*reconciliation|tax\s*reporting|management\s*accounting"
            r"|data\s*cleansing|wire\s*transfers?|ACH|SOP)\b"
        ),
        "certification": (
            r"\b(AWS\s*Certified|Azure\s*Certified|GCP\s*Certified|PMP|PRINCE2"
            r"|Scrum\s*Master|CSM|CISSP|CISA|CPA|CMA|CFA|FRM|ACCA"
            r"|CompTIA|CCNA|CCNP|ITIL|Six\s*Sigma|Lean\s*Six\s*Sigma"
            r"|Google\s*Analytics|TOGAF|SAFe|ISO\s*27001)\b"
        ),
    }

    NORMALIZATION_MAP: dict[str, str] = {
        "reactjs": "React",
        "react.js": "React",
        "vuejs": "Vue.js",
        "vue.js": "Vue.js",
        "nextjs": "Next.js",
        "next.js": "Next.js",
        "nuxtjs": "Nuxt.js",
        "nodejs": "Node.js",
        "node.js": "Node.js",
        "expressjs": "Express.js",
        "express.js": "Express.js",
        "nestjs": "NestJS",
        "typescript": "TypeScript",
        "javascript": "JavaScript",
        "c++": "C++",
        "c#": "C#",
        "asp.net": "ASP.NET",
        ".net": ".NET",
        "spring boot": "Spring Boot",
        "power bi": "Power BI",
        "scikit-learn": "Scikit-learn",
        "tensorflow": "TensorFlow",
        "pytorch": "PyTorch",
        "postgresql": "PostgreSQL",
        "mysql": "MySQL",
        "mongodb": "MongoDB",
        "dynamodb": "DynamoDB",
        "graphql": "GraphQL",
        "rest api": "REST API",
        "rest apis": "REST APIs",
        "ci/cd": "CI/CD",
        "devops": "DevOps",
        "mlops": "MLOps",
        "nlp": "NLP",
        "qa": "QA",
        "bpo": "BPO",
        "js": "JavaScript",
        "ts": "TypeScript",
        "py": "Python",
        "k8s": "Kubernetes",
        "tf": "Terraform",
        "gcp": "GCP",
        "aws": "AWS",
        "seo": "SEO",
        "sem": "SEM",
        "a/b testing": "A/B Testing",
        "tailwind css": "Tailwind CSS",
        "react native": "React Native",
        # Finance / ERP normalization
        "gaap": "GAAP",
        "ifrs": "IFRS",
        "vat": "VAT",
        "gst": "GST",
        "wht": "WHT",
        "sut": "SUT",
        "ach": "ACH",
        "sop": "SOP",
        "erp": "ERP",
        "safe": "SAFe",
        "sap": "SAP",
        "oracle": "Oracle",
        "ms office": "MS Office",
        "visual basic": "Visual Basic",
        "sap ariba": "SAP Ariba",
        "sap concur": "SAP Concur",
        "sap s/4hana": "SAP S/4HANA",
        "sap s4/hana": "SAP S/4HANA",
        "sap business suite": "SAP Business Suite",
        "oracle netsuite": "Oracle NetSuite",
        "oracle ebs": "Oracle EBS",
        "onesource": "OneSource",
        "sherlock system": "Sherlock System",
        "accounts payable": "Accounts Payable",
        "vendor master data": "Vendor Master Data",
        "supplier master data": "Supplier Master Data",
        "tax compliance": "Tax Compliance",
        "tax reconciliation": "Tax Reconciliation",
        "indirect tax": "Indirect Tax",
        "indirect taxes": "Indirect Tax",
        "wire transfer": "Wire Transfer",
        "wire transfers": "Wire Transfer",
        "process improvement": "Process Improvement",
        "process optimization": "Process Optimization",
        "process standardization": "Process Standardization",
        "regulatory compliance": "Regulatory Compliance",
        "data cleansing": "Data Cleansing",
        "management accounting": "Management Accounting",
        "invoice processing": "Invoice Processing",
        "tax reporting": "Tax Reporting",
        "leadership": "Leadership",
        "cost savings": "Cost Savings",
        "compliance": "Compliance",
        "accounting": "Accounting",
        "testing": "Testing",
        "training": "Training",
    }

    # Words that are too ambiguous on their own — only extract if they appear in
    # the explicit skills section or have a skill-indicating surrounding context.
    AMBIGUOUS_SKILLS: set[str] = {
        "banking", "networking", "training", "analytics", "testing",
        "compliance", "accounting", "audit", "auditing",
    }

    # Achievement/outcome phrases that look like skills but aren't
    NON_SKILLS: set[str] = {
        "cost savings", "cost reduction", "revenue growth",
    }

    # Negative-context patterns: if the match span sits inside one of these
    # broader phrases it is NOT a real skill mention.
    NEGATIVE_CONTEXT: list[re.Pattern] = [
        # Product / service names, not skills
        re.compile(r"SAFE\s+Transmission", re.IGNORECASE),
        re.compile(r"Commercial\s+Electronic\s+Banking", re.IGNORECASE),
        re.compile(r"Basic\s+Banking", re.IGNORECASE),
        # Event / webinar titles — skill words inside these aren't skills
        re.compile(r"Networking\s+Event", re.IGNORECASE),
        re.compile(r"Webinar\s*[-–—:]\s*[^\n]+", re.IGNORECASE),
        # "Training Lead" → leadership/training delivery, not "Training" domain
        re.compile(r"Training\s+Lead", re.IGNORECASE),
    ]

    # Section confidence weights
    SECTION_CONFIDENCE: dict[str, float] = {
        "skills_section": 0.95,
        "experience": 0.88,
        "summary": 0.85,
        "education": 0.75,
        "certifications": 0.90,
        "events": 0.55,  # webinars, conferences
        "_default": 0.80,
    }

    def __init__(self, spacy_model: str = "en_core_web_sm"):
        self._taxonomy_categories: dict[str, str] = {}
        self.nlp = self._load_spacy(spacy_model)
        self._add_skill_patterns()

    def _load_spacy(self, model_name: str) -> Language:
        try:
            return spacy.load(model_name, disable=["parser", "lemmatizer"])
        except OSError:
            return spacy.blank("en")

    def _add_skill_patterns(self):
        taxonomy_path = Path(__file__).parent.parent / "data" / "skills_taxonomy.json"
        if not taxonomy_path.exists():
            return

        with open(taxonomy_path) as f:
            taxonomy = json.load(f)

        ruler = self.nlp.add_pipe("entity_ruler", before="ner" if "ner" in self.nlp.pipe_names else None)
        patterns = []
        for entry in taxonomy:
            pattern_def = entry.get("pattern")
            category = entry.get("category", "technical")
            if isinstance(pattern_def, str):
                patterns.append({"label": "SKILL", "pattern": pattern_def})
                self._taxonomy_categories[pattern_def.lower()] = category
            elif isinstance(pattern_def, list):
                patterns.append({"label": "SKILL", "pattern": pattern_def})
                # Build a lowercase key from the token list for categorization
                parts = []
                for tok in pattern_def:
                    if "LOWER" in tok:
                        parts.append(tok["LOWER"])
                    elif "TEXT" in tok:
                        parts.append(tok["TEXT"].lower())
                if parts:
                    self._taxonomy_categories[" ".join(parts)] = category
        ruler.add_patterns(patterns)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_skills(self, text: str, sections: dict | None = None) -> list[dict]:
        """Extract skills from resume text.

        Args:
            text: Full resume text.
            sections: Optional parsed sections dict from ResumeParser.parse_sections().
                      When provided, enables section-aware confidence scoring.
        """
        if sections:
            skills = self._extract_section_aware(text, sections)
            if skills:
                return skills
            # Fall back to flat extraction if section-aware found nothing
            # (e.g. unconventional resume with no recognizable section headers)
        return self._extract_flat(text)

    # ------------------------------------------------------------------
    # Flat extraction (legacy / fallback)
    # ------------------------------------------------------------------

    def _extract_flat(self, text: str) -> list[dict]:
        skills: list[dict] = []
        seen: set[str] = set()
        negative_spans = self._build_negative_spans(text)

        # Layer 1: SpaCy NER + entity ruler
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "SKILL":
                if self._in_negative_span(ent.start_char, ent.end_char, negative_spans):
                    continue
                name = self._normalize(ent.text)
                key = name.lower()
                if key in self.NON_SKILLS:
                    continue
                if key not in seen:
                    seen.add(key)
                    skills.append({
                        "name": name,
                        "category": self._categorize(name),
                        "confidence": 0.90,
                        "source": "ner",
                    })

        # Layer 2: Regex patterns
        for category, pattern in self.TECH_PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                if self._in_negative_span(match.start(), match.end(), negative_spans):
                    continue
                name = self._normalize(match.group())
                key = name.lower()
                if key in self.NON_SKILLS:
                    continue
                # SAFe certification: require exact casing (not "SAFE" product)
                if key == "safe" and category == "certification":
                    if match.group() not in ("SAFe",):
                        continue
                if key not in seen:
                    seen.add(key)
                    skills.append({
                        "name": name,
                        "category": category,
                        "confidence": 0.85,
                        "source": "regex",
                    })

        return skills

    # ------------------------------------------------------------------
    # Section-aware extraction
    # ------------------------------------------------------------------

    def _extract_section_aware(self, full_text: str, sections: dict) -> list[dict]:
        seen: set[str] = set()
        skills: list[dict] = []

        # Build section text blocks with their confidence levels
        section_blocks = self._build_section_blocks(full_text, sections)

        for section_name, section_text, base_confidence in section_blocks:
            is_events = section_name == "events"
            is_skills_section = section_name == "skills_section"
            negative_spans = self._build_negative_spans(section_text)

            # Layer 1: SpaCy NER
            doc = self.nlp(section_text)
            for ent in doc.ents:
                if ent.label_ != "SKILL":
                    continue
                if self._in_negative_span(ent.start_char, ent.end_char, negative_spans):
                    continue
                name = self._normalize(ent.text)
                key = name.lower()
                if key in self.NON_SKILLS:
                    continue
                # Skip ambiguous single-word skills in non-skills sections
                if key in self.AMBIGUOUS_SKILLS and not is_skills_section:
                    if is_events:
                        continue  # Never extract ambiguous skills from events
                    # In experience, only extract if mentioned 2+ times in this section
                    count = len(re.findall(r'\b' + re.escape(ent.text) + r'\b', section_text, re.IGNORECASE))
                    if count < 2:
                        continue
                if key not in seen:
                    seen.add(key)
                    skills.append({
                        "name": name,
                        "category": self._categorize(name),
                        "confidence": base_confidence,
                        "source": "ner",
                    })

            # Layer 2: Regex
            for category, pattern in self.TECH_PATTERNS.items():
                for match in re.finditer(pattern, section_text, re.IGNORECASE):
                    if self._in_negative_span(match.start(), match.end(), negative_spans):
                        continue
                    name = self._normalize(match.group())
                    key = name.lower()
                    if key in self.NON_SKILLS:
                        continue
                    if key in self.AMBIGUOUS_SKILLS and not is_skills_section:
                        if is_events:
                            continue
                        count = len(re.findall(r'\b' + re.escape(match.group()) + r'\b', section_text, re.IGNORECASE))
                        if count < 2:
                            continue
                    # SAFe certification: require exact casing (not "SAFE" product)
                    if key == "safe" and category == "certification":
                        if match.group() not in ("SAFe",):
                            continue
                    if key not in seen:
                        seen.add(key)
                        skills.append({
                            "name": name,
                            "category": category,
                            "confidence": base_confidence,
                            "source": "regex",
                        })

        return skills

    def _build_section_blocks(self, full_text: str, sections: dict) -> list[tuple[str, str, float]]:
        """Return (section_name, section_text, confidence) tuples."""
        blocks: list[tuple[str, str, float]] = []

        # Skills section (highest confidence — explicitly listed by the candidate)
        skills_items = sections.get("skills_section", [])
        if skills_items:
            skills_text = "\n".join(skills_items) if isinstance(skills_items, list) else str(skills_items)
            blocks.append(("skills_section", skills_text, self.SECTION_CONFIDENCE["skills_section"]))

        # Work experience
        experience = sections.get("experience", [])
        if experience:
            exp_parts = []
            for entry in experience:
                if isinstance(entry, dict):
                    if entry.get("title"):
                        exp_parts.append(entry["title"])
                    exp_parts.extend(entry.get("details", []))
                else:
                    exp_parts.append(str(entry))
            if exp_parts:
                blocks.append(("experience", "\n".join(exp_parts), self.SECTION_CONFIDENCE["experience"]))

        # Education
        education = sections.get("education", [])
        if education:
            edu_parts = []
            for entry in education:
                if isinstance(entry, dict):
                    edu_parts.append(entry.get("text", ""))
                else:
                    edu_parts.append(str(entry))
            if edu_parts:
                blocks.append(("education", "\n".join(edu_parts), self.SECTION_CONFIDENCE["education"]))

        # Events / webinars / conferences
        events = sections.get("events", [])
        if events:
            events_text = "\n".join(events) if isinstance(events, list) else str(events)
            blocks.append(("events", events_text, self.SECTION_CONFIDENCE["events"]))
        else:
            # Fallback: scan full text for events section if parser didn't detect one
            events_text = self._extract_events_section(full_text)
            if events_text:
                blocks.append(("events", events_text, self.SECTION_CONFIDENCE["events"]))

        # Summary
        summary = sections.get("summary", "")
        if summary:
            blocks.append(("summary", summary, self.SECTION_CONFIDENCE["summary"]))

        return blocks

    def _extract_events_section(self, text: str) -> str:
        """Extract webinar / conference / relevant experience sections."""
        lines = text.split("\n")
        event_pattern = re.compile(
            r"(?i)\b(relevant\s+experience|conferences?|webinars?|events?|"
            r"professional\s+development|seminars?)\b"
        )
        in_section = False
        event_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if event_pattern.match(stripped) and len(stripped) < 60:
                in_section = True
                continue
            elif in_section:
                # Check if we hit another section header
                if re.match(r"(?i)^[A-Z][A-Z\s&]{2,}$", stripped) and len(stripped) < 60:
                    break
                event_lines.append(stripped)
        return "\n".join(event_lines)

    # ------------------------------------------------------------------
    # Negative-context filtering
    # ------------------------------------------------------------------

    def _build_negative_spans(self, text: str) -> list[tuple[int, int]]:
        """Find character spans where skill matches should be suppressed."""
        spans = []
        for pattern in self.NEGATIVE_CONTEXT:
            for m in pattern.finditer(text):
                spans.append((m.start(), m.end()))
        return spans

    def _in_negative_span(self, start: int, end: int, spans: list[tuple[int, int]]) -> bool:
        """Check if a match [start, end) overlaps any negative span."""
        for ns, ne in spans:
            if start >= ns and end <= ne:
                return True
        return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalize(self, text: str) -> str:
        cleaned = text.strip()
        key = cleaned.lower()
        return self.NORMALIZATION_MAP.get(key, cleaned)

    def _categorize(self, skill_name: str) -> str:
        key = skill_name.lower()
        # Check taxonomy first (most comprehensive)
        if key in self._taxonomy_categories:
            return self._taxonomy_categories[key]
        # Fall back to regex patterns
        for category, pattern in self.TECH_PATTERNS.items():
            if re.search(pattern, skill_name, re.IGNORECASE):
                return category
        return "technical"
