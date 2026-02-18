import json
import re
from pathlib import Path

import spacy
from spacy.language import Language


class SkillExtractor:
    TECH_PATTERNS: dict[str, str] = {
        "technical": (
            r"\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Ruby|PHP|Swift|Kotlin"
            r"|Scala|R|MATLAB|SQL|HTML|CSS|Sass|LESS|Perl|Lua|Dart|Elixir|Haskell"
            r"|Shell|Bash|PowerShell|VBA|ABAP|COBOL|Fortran)\b"
        ),
        "framework": (
            r"\b(React|Angular|Vue\.?js|Next\.?js|Nuxt\.?js|Svelte|Django|Flask|FastAPI"
            r"|Spring\s*Boot|\.NET|ASP\.NET|Node\.?js|Express\.?js|NestJS|Rails"
            r"|Laravel|Symfony|TensorFlow|PyTorch|Keras|Scikit-learn|Pandas|NumPy"
            r"|Matplotlib|Seaborn|Plotly|Streamlit|Gradio|LangChain)\b"
        ),
        "tool": (
            r"\b(Docker|Kubernetes|Git|GitHub|GitLab|Bitbucket|AWS|Azure|GCP"
            r"|Jenkins|CircleCI|Travis\s*CI|Terraform|Ansible|Puppet|Chef"
            r"|Figma|Sketch|Adobe\s*XD|Photoshop|Illustrator"
            r"|Tableau|Power\s*BI|Looker|Metabase|Grafana"
            r"|Jira|Confluence|Slack|Trello|Notion|Asana"
            r"|Postman|Swagger|Nginx|Apache|Redis|RabbitMQ|Kafka"
            r"|MongoDB|PostgreSQL|MySQL|SQLite|Oracle|DynamoDB|Cassandra"
            r"|Elasticsearch|Supabase|Firebase|Vercel|Netlify|Heroku"
            r"|SAP|QuickBooks|Xero|Sage|Tally|Zoho)\b"
        ),
        "soft": (
            r"\b(leadership|communication|teamwork|team\s*work|problem[- ]solving"
            r"|critical\s*thinking|project\s*management|time\s*management"
            r"|adaptability|creativity|collaboration|mentoring|coaching"
            r"|presentation|negotiation|conflict\s*resolution"
            r"|strategic\s*planning|decision[- ]making|analytical\s*thinking)\b"
        ),
        "domain": (
            r"\b(machine\s*learning|deep\s*learning|natural\s*language\s*processing|NLP"
            r"|computer\s*vision|data\s*science|data\s*engineering|data\s*analytics"
            r"|business\s*intelligence|DevOps|MLOps|CI/CD|microservices"
            r"|REST\s*API|GraphQL|web\s*scraping|ETL|data\s*warehousing"
            r"|agile|scrum|kanban|lean|six\s*sigma"
            r"|financial\s*analysis|tax\s*compliance|auditing|bookkeeping"
            r"|accounting|budgeting|forecasting|financial\s*reporting"
            r"|BPO|customer\s*service|quality\s*assurance|QA|testing)\b"
        ),
        "certification": (
            r"\b(AWS\s*Certified|Azure\s*Certified|GCP\s*Certified|PMP|PRINCE2"
            r"|Scrum\s*Master|CSM|CISSP|CISA|CPA|CMA|CFA|FRM|ACCA"
            r"|CompTIA|CCNA|CCNP|ITIL|Six\s*Sigma|Lean\s*Six\s*Sigma"
            r"|Google\s*Analytics|HubSpot|Salesforce)\b"
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
    }

    def __init__(self, spacy_model: str = "en_core_web_sm"):
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
            if isinstance(pattern_def, str):
                patterns.append({"label": "SKILL", "pattern": pattern_def})
            elif isinstance(pattern_def, list):
                patterns.append({"label": "SKILL", "pattern": pattern_def})
        ruler.add_patterns(patterns)

    def extract_skills(self, text: str) -> list[dict]:
        skills: list[dict] = []
        seen: set[str] = set()

        # Layer 1: SpaCy NER + entity ruler
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "SKILL":
                name = self._normalize(ent.text)
                if name.lower() not in seen:
                    seen.add(name.lower())
                    skills.append({
                        "name": name,
                        "category": self._categorize(name),
                        "confidence": 0.90,
                        "source": "ner",
                    })

        # Layer 2: Regex patterns
        for category, pattern in self.TECH_PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                name = self._normalize(match.group())
                if name.lower() not in seen:
                    seen.add(name.lower())
                    skills.append({
                        "name": name,
                        "category": category,
                        "confidence": 0.85,
                        "source": "regex",
                    })

        return skills

    def _normalize(self, text: str) -> str:
        cleaned = text.strip()
        key = cleaned.lower()
        return self.NORMALIZATION_MAP.get(key, cleaned)

    def _categorize(self, skill_name: str) -> str:
        key = skill_name.lower()
        for category, pattern in self.TECH_PATTERNS.items():
            if re.search(pattern, skill_name, re.IGNORECASE):
                return category
        return "technical"
