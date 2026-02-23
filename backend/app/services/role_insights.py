"""Role insights — generates day-in-the-life content, role comparisons,
and enriched role information using LLM providers."""

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.ai.provider_factory import ProviderFactory

logger = logging.getLogger(__name__)


class RoleInsightsService:
    async def get_day_in_life(self, db: AsyncSession, role_id: int) -> dict:
        """Generate a 'day in the life' description for a role."""
        result = await db.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()
        if not role:
            return {"error": "Role not found"}

        required = json.loads(role.required_skills) if role.required_skills else []
        preferred = json.loads(role.preferred_skills) if role.preferred_skills else []

        # Try LLM generation first
        day_content = await self._generate_day_in_life_llm(role, required, preferred)
        if day_content:
            return day_content

        # Fallback: template-based
        return self._generate_day_in_life_template(role, required, preferred)

    async def _generate_day_in_life_llm(
        self, role: Role, required: list, preferred: list
    ) -> dict | None:
        """Use LLM to generate rich day-in-the-life content."""
        try:
            provider = ProviderFactory.get_provider("fast")
        except RuntimeError:
            return None

        prompt = (
            f"Generate a realistic 'Day in the Life' description for a {role.title} "
            f"({role.seniority} level) in the Philippines. "
            f"The role is in the {role.category} category.\n"
            f"Required skills: {', '.join(required[:8])}\n"
            f"Preferred skills: {', '.join(preferred[:5])}\n\n"
            f"Provide:\n"
            f"1. A typical daily schedule (6-8 time blocks from morning to evening)\n"
            f"2. Common tools used daily (3-5 tools)\n"
            f"3. Who they typically work with (2-4 team types)\n"
            f"4. Biggest challenges (2-3)\n"
            f"5. Most rewarding aspects (2-3)\n\n"
            f"Format as JSON with keys: schedule (array of {{time, activity}}), "
            f"daily_tools, team_interactions, challenges, rewards"
        )

        try:
            result = await provider.generate_structured(
                prompt,
                schema={
                    "schedule": [{"time": "str", "activity": "str"}],
                    "daily_tools": ["str"],
                    "team_interactions": ["str"],
                    "challenges": ["str"],
                    "rewards": ["str"],
                },
                system_prompt=(
                    "You are a career counselor helping people understand what different "
                    "jobs are really like in the Philippine market. Be specific and realistic."
                ),
            )

            return {
                "role_id": role.id,
                "role_title": role.title,
                "source": "ai_generated",
                **result,
            }
        except Exception as e:
            logger.warning(f"LLM day-in-life generation failed for {role.title}: {e}")
            return None

    def _generate_day_in_life_template(
        self, role: Role, required: list, preferred: list
    ) -> dict:
        """Template-based fallback for day-in-the-life content."""
        seniority = role.seniority or "mid"
        category = role.category or "Engineering"

        # Time blocks based on seniority
        if seniority in ("entry", "mid"):
            schedule = [
                {"time": "9:00 AM", "activity": "Check emails and messages, review task board"},
                {"time": "9:30 AM", "activity": f"Daily standup with team"},
                {"time": "10:00 AM", "activity": f"Focus work on core {category.lower()} tasks"},
                {"time": "12:00 PM", "activity": "Lunch break"},
                {"time": "1:00 PM", "activity": "Collaboration: code reviews, design sessions, or meetings"},
                {"time": "3:00 PM", "activity": "Deep work: building features or solving problems"},
                {"time": "5:00 PM", "activity": "Documentation, knowledge sharing, or learning"},
                {"time": "6:00 PM", "activity": "Wrap up, update task status, plan tomorrow"},
            ]
        elif seniority == "senior":
            schedule = [
                {"time": "9:00 AM", "activity": "Review PRs/deliverables, respond to technical questions"},
                {"time": "9:30 AM", "activity": "Team standup and sprint planning"},
                {"time": "10:00 AM", "activity": "Architecture discussions or technical design"},
                {"time": "11:30 AM", "activity": "Mentoring junior team members"},
                {"time": "12:00 PM", "activity": "Lunch break"},
                {"time": "1:00 PM", "activity": "Cross-team alignment meetings"},
                {"time": "2:30 PM", "activity": "Deep technical work and problem solving"},
                {"time": "5:00 PM", "activity": "Technical documentation and knowledge transfer"},
            ]
        else:  # lead, executive
            schedule = [
                {"time": "9:00 AM", "activity": "Review metrics, dashboards, and team status"},
                {"time": "9:30 AM", "activity": "Leadership standup and priority alignment"},
                {"time": "10:00 AM", "activity": "Stakeholder meetings and strategic discussions"},
                {"time": "11:30 AM", "activity": "1-on-1s with direct reports"},
                {"time": "12:00 PM", "activity": "Lunch (often working lunch with partners)"},
                {"time": "1:00 PM", "activity": "Cross-departmental planning sessions"},
                {"time": "3:00 PM", "activity": "Process improvement and strategic initiatives"},
                {"time": "5:00 PM", "activity": "End-of-day review, planning, async communication"},
            ]

        # Tools based on category
        tool_map = {
            "Engineering": ["VS Code / IDE", "Git & GitHub", "Jira / Linear", "Slack", "Docker"],
            "Data": ["Python / Jupyter", "SQL Client", "Tableau / Power BI", "Git", "Slack"],
            "Product": ["Figma", "Jira", "Confluence", "Slack", "Google Analytics"],
            "Design": ["Figma", "Adobe Creative Suite", "Miro", "Slack", "Notion"],
            "Finance": ["Excel / Google Sheets", "SAP / ERP", "Power BI", "Email", "Accounting Software"],
            "Marketing": ["Google Analytics", "SEMrush / Ahrefs", "Canva", "HubSpot", "Social Media Tools"],
            "HR": ["HRIS Software", "LinkedIn Recruiter", "Excel", "Slack", "ATS Platform"],
            "Sales": ["CRM (Salesforce / HubSpot)", "Email", "Video Conferencing", "Excel", "Sales Navigator"],
        }
        daily_tools = tool_map.get(category, ["Slack", "Email", "Project Management Tool", "Browser", "Documents"])

        return {
            "role_id": role.id,
            "role_title": role.title,
            "source": "template",
            "schedule": schedule,
            "daily_tools": daily_tools,
            "team_interactions": self._get_team_interactions(category, seniority),
            "challenges": self._get_challenges(category, seniority),
            "rewards": self._get_rewards(category, seniority),
        }

    def _get_team_interactions(self, category: str, seniority: str) -> list[str]:
        base = {
            "Engineering": ["Product managers", "Designers", "QA/Testing team", "DevOps"],
            "Data": ["Business stakeholders", "Engineering team", "Product managers", "Analysts"],
            "Product": ["Engineering team", "Design team", "Business stakeholders", "Users"],
            "Design": ["Product managers", "Engineers", "User researchers", "Content team"],
            "Finance": ["Business units", "Auditors", "Management", "Tax consultants"],
            "Marketing": ["Sales team", "Design team", "Content creators", "Analytics team"],
            "HR": ["Hiring managers", "Employees", "Legal team", "External recruiters"],
            "Sales": ["Marketing team", "Customer success", "Product team", "Finance"],
        }
        interactions = base.get(category, ["Team members", "Managers", "Stakeholders"])

        if seniority in ("lead", "executive"):
            interactions.extend(["Executive team", "Board / investors"])
        return interactions[:5]

    def _get_challenges(self, category: str, seniority: str) -> list[str]:
        challenges = {
            "Engineering": [
                "Balancing technical debt with new feature development",
                "Keeping up with rapidly evolving technologies",
                "Debugging complex production issues under time pressure",
            ],
            "Data": [
                "Working with messy, incomplete, or inconsistent data",
                "Communicating technical findings to non-technical stakeholders",
                "Balancing speed of insights vs. accuracy of analysis",
            ],
            "Product": [
                "Prioritizing features with limited resources",
                "Aligning different stakeholder interests",
                "Making decisions with incomplete information",
            ],
            "Finance": [
                "Meeting tight regulatory deadlines",
                "Maintaining accuracy with large data volumes",
                "Adapting to changing tax and compliance requirements",
            ],
        }
        return challenges.get(category, [
            "Meeting deadlines while maintaining quality",
            "Adapting to changing requirements",
            "Balancing multiple priorities simultaneously",
        ])

    def _get_rewards(self, category: str, seniority: str) -> list[str]:
        rewards = {
            "Engineering": [
                "Seeing your code used by real users",
                "Solving complex technical puzzles",
                "Continuous learning and skill growth",
            ],
            "Data": [
                "Uncovering insights that drive business decisions",
                "Building models that create real-world impact",
                "Working at the intersection of technology and business",
            ],
            "Product": [
                "Shaping products that improve people's lives",
                "Seeing user satisfaction from your product decisions",
                "Working with diverse, cross-functional teams",
            ],
            "Finance": [
                "Contributing to organizational financial health",
                "Clear career progression path (CPA, CFA)",
                "Working with numbers and analytical problem-solving",
            ],
        }
        return rewards.get(category, [
            "Making a tangible impact on the organization",
            "Continuous professional development",
            "Collaborating with talented colleagues",
        ])

    async def compare_roles(
        self, db: AsyncSession, role_id_a: int, role_id_b: int
    ) -> dict:
        """Compare two roles side by side."""
        result_a = await db.execute(select(Role).where(Role.id == role_id_a))
        result_b = await db.execute(select(Role).where(Role.id == role_id_b))
        role_a = result_a.scalar_one_or_none()
        role_b = result_b.scalar_one_or_none()

        if not role_a or not role_b:
            return {"error": "One or both roles not found"}

        skills_a = set(json.loads(role_a.required_skills or "[]"))
        skills_b = set(json.loads(role_b.required_skills or "[]"))
        shared = skills_a & skills_b
        only_a = skills_a - skills_b
        only_b = skills_b - skills_a

        return {
            "role_a": {"id": role_a.id, "title": role_a.title, "category": role_a.category},
            "role_b": {"id": role_b.id, "title": role_b.title, "category": role_b.category},
            "comparison": {
                "salary": {
                    "a": role_a.salary_range_ph,
                    "b": role_b.salary_range_ph,
                    "higher": "a" if (role_a.salary_max_ph or 0) > (role_b.salary_max_ph or 0) else "b",
                },
                "seniority": {"a": role_a.seniority, "b": role_b.seniority},
                "experience_required": {
                    "a": role_a.min_years_experience,
                    "b": role_b.min_years_experience,
                },
                "demand": {
                    "a": role_a.demand_score,
                    "b": role_b.demand_score,
                    "higher": "a" if (role_a.demand_score or 0) > (role_b.demand_score or 0) else "b",
                },
                "growth_potential": {
                    "a": role_a.growth_potential,
                    "b": role_b.growth_potential,
                    "higher": "a" if (role_a.growth_potential or 0) > (role_b.growth_potential or 0) else "b",
                },
                "remote_friendly": {"a": role_a.remote_friendly, "b": role_b.remote_friendly},
                "shared_skills": sorted(shared),
                "unique_to_a": sorted(only_a),
                "unique_to_b": sorted(only_b),
                "skill_transferability": round(
                    len(shared) / max(1, len(skills_a | skills_b)) * 100, 1
                ),
            },
        }
