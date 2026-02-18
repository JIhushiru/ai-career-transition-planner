import re


class ResumeParser:
    SECTION_HEADERS = {
        "summary": r"(?i)\b(summary|profile|objective|about\s*me|professional\s*summary)\b",
        "experience": r"(?i)\b(experience|work\s*history|employment|professional\s*experience|work\s*experience)\b",
        "education": r"(?i)\b(education|academic|qualifications|degrees?)\b",
        "skills_section": r"(?i)\b(skills|technical\s*skills|core\s*competencies|competencies|expertise|proficiencies)\b",
        "certifications": r"(?i)\b(certifications?|licenses?|credentials?)\b",
        "projects": r"(?i)\b(projects|portfolio)\b",
    }

    EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
    PHONE_PATTERN = re.compile(
        r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
    )
    LINKEDIN_PATTERN = re.compile(r"linkedin\.com/in/[\w-]+", re.IGNORECASE)

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        import fitz

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text("text"))
        doc.close()
        return "\n".join(text_parts)

    def parse_sections(self, raw_text: str) -> dict:
        return {
            "contact": self._extract_contact(raw_text),
            "summary": self._extract_section(raw_text, "summary"),
            "experience": self._extract_experience_entries(raw_text),
            "education": self._extract_education_entries(raw_text),
            "skills_section": self._extract_skills_list(raw_text),
        }

    def _extract_contact(self, text: str) -> dict:
        contact = {}
        emails = self.EMAIL_PATTERN.findall(text)
        if emails:
            contact["email"] = emails[0]

        phones = self.PHONE_PATTERN.findall(text)
        if phones:
            contact["phone"] = phones[0].strip()

        linkedin = self.LINKEDIN_PATTERN.findall(text)
        if linkedin:
            contact["linkedin"] = linkedin[0]

        lines = text.strip().split("\n")
        if lines:
            first_line = lines[0].strip()
            if first_line and not self.EMAIL_PATTERN.search(first_line):
                contact["name"] = first_line

        return contact

    def _find_section_bounds(self, text: str) -> list[tuple[str, int, int]]:
        lines = text.split("\n")
        sections = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            for section_name, pattern in self.SECTION_HEADERS.items():
                if re.match(pattern, stripped) and len(stripped) < 60:
                    sections.append((section_name, i, -1))
                    break

        result = []
        for idx, (name, start, _) in enumerate(sections):
            end = sections[idx + 1][1] if idx + 1 < len(sections) else len(lines)
            result.append((name, start, end))

        return result

    def _extract_section(self, text: str, section_name: str) -> str:
        lines = text.split("\n")
        bounds = self._find_section_bounds(text)
        for name, start, end in bounds:
            if name == section_name:
                section_lines = lines[start + 1 : end]
                return "\n".join(line.strip() for line in section_lines if line.strip())
        return ""

    def _extract_experience_entries(self, text: str) -> list[dict]:
        raw = self._extract_section(text, "experience")
        if not raw:
            return []

        entries = []
        date_pattern = re.compile(
            r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*[\s.,-]*\d{4})"
            r"\s*[-–to]+\s*"
            r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*[\s.,-]*\d{4}|[Pp]resent|[Cc]urrent)",
            re.IGNORECASE,
        )

        current_entry: dict | None = None
        for line in raw.split("\n"):
            line = line.strip()
            if not line:
                continue

            date_match = date_pattern.search(line)
            if date_match or (len(line) < 80 and not line.startswith(("•", "-", "*", "–"))):
                if current_entry and current_entry.get("title"):
                    entries.append(current_entry)
                current_entry = {
                    "title": line,
                    "dates": date_match.group(0) if date_match else "",
                    "details": [],
                }
            elif current_entry is not None:
                cleaned = re.sub(r"^[•\-*–]\s*", "", line)
                if cleaned:
                    current_entry["details"].append(cleaned)

        if current_entry and current_entry.get("title"):
            entries.append(current_entry)

        return entries

    def _extract_education_entries(self, text: str) -> list[dict]:
        raw = self._extract_section(text, "education")
        if not raw:
            return []

        entries = []
        for line in raw.split("\n"):
            line = line.strip()
            if line:
                entries.append({"text": line})
        return entries

    def _extract_skills_list(self, text: str) -> list[str]:
        raw = self._extract_section(text, "skills_section")
        if not raw:
            return []

        skills = []
        for line in raw.split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = re.split(r"[,;|•·]", line)
            for part in parts:
                cleaned = part.strip().strip("-").strip("*").strip()
                if cleaned and len(cleaned) < 50:
                    skills.append(cleaned)

        return skills
