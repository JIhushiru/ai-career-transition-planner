"""Dream Job Reverse Engineering — given a dream role, builds a complete
step-by-step plan including path, skills, timeline, weekly actions, interview
prep, and portfolio projects."""

import json
import logging
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_graph import CareerTransition
from app.models.role import Role
from app.models.skill import Skill, UserSkill
from app.services.career_graph import CareerGraphService
from app.services.roadmap_generator import RoadmapGenerator

logger = logging.getLogger(__name__)

graph_service = CareerGraphService()
roadmap_gen = RoadmapGenerator()


class DreamJobPlanner:
    async def build_plan(
        self,
        db: AsyncSession,
        user_id: int,
        dream_role_id: int,
        current_role_id: int | None = None,
        user_years: int | None = None,
        current_salary: int | None = None,
    ) -> dict:
        """Build a complete reverse-engineered plan to reach a dream role."""

        # 1. Get dream role details
        result = await db.execute(select(Role).where(Role.id == dream_role_id))
        dream_role = result.scalar_one_or_none()
        if not dream_role:
            return {"error": "Dream role not found"}

        # 2. Get user's current skills
        result = await db.execute(
            select(Skill.name)
            .join(UserSkill, UserSkill.skill_id == Skill.id)
            .where(UserSkill.user_id == user_id)
        )
        user_skills = {row[0] for row in result.all()}
        user_skills_lower = {s.lower() for s in user_skills}

        # 3. Find career path
        paths = []
        if current_role_id:
            paths = await graph_service.find_paths(
                db, current_role_id, dream_role_id, max_steps=5, max_paths=3
            )

        # 4. Analyze skill gaps
        gap_analysis = await roadmap_gen.analyze_skill_gaps(
            db, user_id, dream_role_id
        )

        # 5. Build weekly action plan
        weekly_plan = self._build_weekly_plan(
            gap_analysis.get("skill_gaps", []),
            gap_analysis.get("milestones", []),
        )

        # 6. Generate interview prep topics
        interview_prep = self._generate_interview_prep(dream_role, user_skills)

        # 7. Suggest portfolio projects
        portfolio = self._suggest_portfolio_projects(
            dream_role,
            gap_analysis.get("skill_gaps", []),
            user_skills,
        )

        # 8. Calculate salary trajectory
        salary_trajectory = self._calculate_salary_trajectory(
            paths, current_salary, dream_role, db
        )

        # 9. Format paths with role details
        role_map = await graph_service.get_role_map(db)
        formatted_paths = []
        for path in paths:
            steps = []
            for step in path:
                from_role = role_map.get(step["from_role_id"])
                to_role = role_map.get(step["to_role_id"])
                if from_role and to_role:
                    steps.append({
                        "from_role": from_role.title,
                        "to_role": to_role.title,
                        "difficulty": step["difficulty"],
                        "months": step["months"],
                        "upskills": step["upskills"],
                        "type": step["type"],
                    })
            if steps:
                total_months = sum(s["months"] for s in steps)
                formatted_paths.append({
                    "steps": steps,
                    "total_months": total_months,
                    "total_difficulty": round(
                        sum(s["difficulty"] for s in steps) / len(steps), 2
                    ),
                })

        return {
            "dream_role": {
                "id": dream_role.id,
                "title": dream_role.title,
                "category": dream_role.category,
                "description": dream_role.description,
                "salary_range_ph": dream_role.salary_range_ph,
                "salary_range_usd": dream_role.salary_range_usd,
                "seniority": dream_role.seniority,
                "demand_score": dream_role.demand_score,
                "growth_potential": dream_role.growth_potential,
            },
            "career_paths": formatted_paths,
            "skill_analysis": {
                "current_skills": sorted(user_skills),
                "skills_matched": sorted(gap_analysis.get("existing_skills", [])),
                "skills_to_learn": [
                    {
                        "skill": g["skill"],
                        "priority": g["priority"],
                        "estimated_hours": g["estimated_hours"],
                    }
                    for g in gap_analysis.get("skill_gaps", [])
                ],
                "match_percentage": round(
                    len(gap_analysis.get("existing_skills", []))
                    / max(
                        1,
                        len(gap_analysis.get("existing_skills", []))
                        + len(gap_analysis.get("skill_gaps", [])),
                    )
                    * 100,
                    1,
                ),
                "total_learning_hours": gap_analysis.get("total_estimated_hours", 0),
            },
            "weekly_plan": weekly_plan,
            "interview_prep": interview_prep,
            "portfolio_projects": portfolio,
            "milestones": gap_analysis.get("milestones", []),
        }

    def _build_weekly_plan(
        self, skill_gaps: list[dict], milestones: list[dict]
    ) -> list[dict]:
        """Break down the learning roadmap into actionable weekly plans."""
        weeks = []
        week_num = 1
        today = date.today()

        # Phase 1: Core skills (10 hrs/week pace)
        high_gaps = [g for g in skill_gaps if g["priority"] == "high"]
        medium_gaps = [g for g in skill_gaps if g["priority"] == "medium"]

        # Batch high-priority skills into weekly chunks
        current_batch: list[str] = []
        batch_hours = 0

        for gap in high_gaps:
            skill = gap["skill"]
            hours = gap["estimated_hours"]

            if batch_hours + hours > 10 and current_batch:
                start_date = today + timedelta(weeks=week_num - 1)
                weeks.append({
                    "week": week_num,
                    "start_date": start_date.isoformat(),
                    "phase": "Core Skills",
                    "focus_skills": current_batch,
                    "hours": batch_hours,
                    "actions": [
                        f"Study: {', '.join(current_batch)} ({batch_hours}h)",
                        "Practice with hands-on exercises or tutorials",
                        "Update your resume/LinkedIn with progress",
                    ],
                })
                week_num += 1
                current_batch = []
                batch_hours = 0

            current_batch.append(skill)
            batch_hours += hours

        if current_batch:
            start_date = today + timedelta(weeks=week_num - 1)
            weeks.append({
                "week": week_num,
                "start_date": start_date.isoformat(),
                "phase": "Core Skills",
                "focus_skills": current_batch,
                "hours": batch_hours,
                "actions": [
                    f"Study: {', '.join(current_batch)} ({batch_hours}h)",
                    "Practice with hands-on exercises or tutorials",
                    "Update your resume/LinkedIn with progress",
                ],
            })
            week_num += 1

        # Phase 2: Preferred skills
        current_batch = []
        batch_hours = 0
        for gap in medium_gaps:
            skill = gap["skill"]
            hours = gap["estimated_hours"]

            if batch_hours + hours > 10 and current_batch:
                start_date = today + timedelta(weeks=week_num - 1)
                weeks.append({
                    "week": week_num,
                    "start_date": start_date.isoformat(),
                    "phase": "Expand Skills",
                    "focus_skills": current_batch,
                    "hours": batch_hours,
                    "actions": [
                        f"Learn: {', '.join(current_batch)} ({batch_hours}h)",
                        "Build small side projects using new skills",
                        "Network with professionals in your target role",
                    ],
                })
                week_num += 1
                current_batch = []
                batch_hours = 0

            current_batch.append(skill)
            batch_hours += hours

        if current_batch:
            start_date = today + timedelta(weeks=week_num - 1)
            weeks.append({
                "week": week_num,
                "start_date": start_date.isoformat(),
                "phase": "Expand Skills",
                "focus_skills": current_batch,
                "hours": batch_hours,
                "actions": [
                    f"Learn: {', '.join(current_batch)} ({batch_hours}h)",
                    "Build small side projects using new skills",
                    "Network with professionals in your target role",
                ],
            })
            week_num += 1

        # Phase 3: Portfolio & job prep
        for i in range(4):
            start_date = today + timedelta(weeks=week_num - 1)
            if i < 2:
                actions = [
                    "Build or finish a portfolio project",
                    "Write about your project (blog post or README)",
                    "Share progress on LinkedIn or GitHub",
                ]
                phase = "Portfolio Building"
            else:
                actions = [
                    "Practice interview questions for your target role",
                    "Apply to 2-3 positions or reach out to recruiters",
                    "Do a mock interview or whiteboard session",
                ]
                phase = "Job Preparation"

            weeks.append({
                "week": week_num,
                "start_date": start_date.isoformat(),
                "phase": phase,
                "focus_skills": [],
                "hours": 10,
                "actions": actions,
            })
            week_num += 1

        return weeks

    def _generate_interview_prep(
        self, dream_role: Role, user_skills: set[str]
    ) -> dict:
        """Generate interview preparation topics based on the dream role."""
        required = []
        preferred = []
        if dream_role.required_skills:
            required = json.loads(dream_role.required_skills)
        if dream_role.preferred_skills:
            preferred = json.loads(dream_role.preferred_skills)

        user_lower = {s.lower() for s in user_skills}

        # Technical topics from skills the user needs to prove
        strong_skills = [s for s in required if s.lower() in user_lower]
        weak_skills = [s for s in required if s.lower() not in user_lower]

        # Build interview categories
        behavioral_questions = [
            f"Tell me about a time you used {skill} to solve a complex problem."
            for skill in strong_skills[:3]
        ]
        behavioral_questions.extend([
            "Describe a situation where you had to learn a new technology quickly.",
            "How do you handle disagreements with team members on technical decisions?",
            f"Why are you interested in transitioning to {dream_role.title}?",
            "Tell me about a project you're most proud of and why.",
        ])

        technical_topics = []
        for skill in required[:8]:
            technical_topics.append({
                "skill": skill,
                "strength": "strong" if skill.lower() in user_lower else "gap",
                "prep_tip": (
                    f"Be ready to discuss real projects where you used {skill}."
                    if skill.lower() in user_lower
                    else f"Study {skill} fundamentals and build a practice project."
                ),
            })

        role_specific = []
        seniority = dream_role.seniority or "mid"
        if seniority in ("senior", "lead", "executive"):
            role_specific.extend([
                "System design and architecture questions",
                "Leadership and mentoring scenarios",
                "Technical decision-making trade-offs",
            ])
        if seniority in ("lead", "executive"):
            role_specific.extend([
                "Team management and hiring experience",
                "Strategic planning and roadmapping",
                "Stakeholder communication",
            ])

        category = dream_role.category or ""
        if category == "Engineering":
            role_specific.extend([
                "Coding challenges (LeetCode medium-hard level)",
                "Code review scenarios",
                "Performance optimization discussions",
            ])
        elif category == "Data":
            role_specific.extend([
                "SQL queries and data modeling questions",
                "Statistics and probability concepts",
                "Data pipeline design discussions",
            ])
        elif category == "Product":
            role_specific.extend([
                "Product sense and prioritization frameworks",
                "Metrics definition and A/B testing",
                "User research methodology",
            ])
        elif category in ("Finance", "Consulting"):
            role_specific.extend([
                "Case study and analytical problem-solving",
                "Financial modeling scenarios",
                "Industry knowledge questions",
            ])

        return {
            "behavioral_questions": behavioral_questions,
            "technical_topics": technical_topics,
            "role_specific_areas": role_specific,
            "preparation_tips": [
                "Research the company and its tech stack before the interview",
                f"Prepare a 2-minute pitch explaining your transition to {dream_role.title}",
                "Have 3 strong STAR stories ready (Situation, Task, Action, Result)",
                "Prepare thoughtful questions to ask the interviewer",
                f"Review common {dream_role.category} interview patterns",
            ],
        }

    def _suggest_portfolio_projects(
        self,
        dream_role: Role,
        skill_gaps: list[dict],
        user_skills: set[str],
    ) -> list[dict]:
        """Suggest portfolio projects that demonstrate readiness for the dream role."""
        required = []
        if dream_role.required_skills:
            required = json.loads(dream_role.required_skills)

        gap_skills = [g["skill"] for g in skill_gaps if g["priority"] == "high"]
        matched_skills = [s for s in required if s.lower() in {sk.lower() for sk in user_skills}]

        projects = []
        category = dream_role.category or ""
        title = dream_role.title or ""
        seniority = dream_role.seniority or "mid"

        # Generate role-specific project suggestions
        if category == "Engineering":
            projects.append({
                "title": f"Full-Stack {title} Portfolio App",
                "description": (
                    f"Build a production-ready web application that showcases the core skills "
                    f"required for {title}. Include authentication, CRUD operations, "
                    f"and deployment to a cloud platform."
                ),
                "skills_demonstrated": (matched_skills + gap_skills)[:6],
                "complexity": "medium" if seniority in ("entry", "mid") else "high",
                "estimated_hours": 40 if seniority in ("entry", "mid") else 60,
            })
            if any(s.lower() in ["system design", "architecture patterns", "distributed systems"]
                   for s in required):
                projects.append({
                    "title": "System Design Documentation",
                    "description": (
                        "Write detailed system design documents for 3 different architectures "
                        "(e.g., URL shortener, chat system, e-commerce platform). "
                        "Include diagrams, trade-off analysis, and scaling considerations."
                    ),
                    "skills_demonstrated": ["System Design", "Technical Writing", "Architecture"],
                    "complexity": "high",
                    "estimated_hours": 30,
                })

        elif category == "Data":
            projects.append({
                "title": "End-to-End Data Pipeline & Dashboard",
                "description": (
                    f"Build a complete data pipeline that ingests, transforms, and visualizes data. "
                    f"Use real-world datasets (e.g., Philippine economic data, job market trends). "
                    f"Deploy a live dashboard."
                ),
                "skills_demonstrated": (matched_skills + gap_skills)[:6],
                "complexity": "medium",
                "estimated_hours": 50,
            })
            if "machine learning" in title.lower() or "data scientist" in title.lower():
                projects.append({
                    "title": "ML Model with Production Deployment",
                    "description": (
                        "Train and deploy a machine learning model as a REST API. "
                        "Include data preprocessing, feature engineering, model evaluation, "
                        "and monitoring. Use a real-world problem relevant to your target industry."
                    ),
                    "skills_demonstrated": ["Machine Learning", "Python", "REST APIs", "Docker"],
                    "complexity": "high",
                    "estimated_hours": 60,
                })

        elif category == "Product":
            projects.append({
                "title": "Product Case Study & Strategy Document",
                "description": (
                    "Write a comprehensive product case study analyzing a real product. "
                    "Include market analysis, user personas, competitive landscape, "
                    "feature prioritization framework, and a product roadmap."
                ),
                "skills_demonstrated": ["Product Strategy", "User Research", "Roadmap Planning"],
                "complexity": "medium",
                "estimated_hours": 25,
            })

        elif category == "Design":
            projects.append({
                "title": "Complete UX Case Study",
                "description": (
                    "Design a complete user experience from research to final UI. "
                    "Include user interviews, personas, wireframes, prototypes, "
                    "usability testing results, and final high-fidelity designs."
                ),
                "skills_demonstrated": (matched_skills + gap_skills)[:5],
                "complexity": "medium",
                "estimated_hours": 40,
            })

        elif category in ("Finance", "Consulting"):
            projects.append({
                "title": "Financial Analysis Report",
                "description": (
                    "Create a detailed financial analysis of a Philippine publicly-listed company. "
                    "Include financial modeling, ratio analysis, valuation, "
                    "and investment recommendations with visualizations."
                ),
                "skills_demonstrated": (matched_skills + gap_skills)[:5],
                "complexity": "medium",
                "estimated_hours": 30,
            })

        elif category in ("Marketing", "Content"):
            projects.append({
                "title": "Digital Marketing Campaign Plan",
                "description": (
                    "Design a complete digital marketing campaign for a local Philippine brand. "
                    "Include target audience analysis, channel strategy, content calendar, "
                    "budget allocation, and KPI tracking dashboard."
                ),
                "skills_demonstrated": (matched_skills + gap_skills)[:5],
                "complexity": "medium",
                "estimated_hours": 25,
            })

        # Universal project: Open source contribution
        projects.append({
            "title": "Open Source Contribution",
            "description": (
                "Contribute to an open source project related to your target role. "
                "Start with documentation or small bug fixes, then work up to feature contributions. "
                "This demonstrates collaboration, code review skills, and community engagement."
            ),
            "skills_demonstrated": ["Git", "Code Review", "Collaboration"],
            "complexity": "low",
            "estimated_hours": 20,
        })

        # Universal project: Personal brand / blog
        projects.append({
            "title": f"Technical Blog: My Journey to {title}",
            "description": (
                f"Write 5-10 blog posts documenting your career transition journey. "
                f"Cover what you're learning, challenges faced, and insights gained. "
                f"Publish on Medium, Dev.to, or a personal site."
            ),
            "skills_demonstrated": ["Technical Writing", "Communication"],
            "complexity": "low",
            "estimated_hours": 15,
        })

        return projects

    def _calculate_salary_trajectory(
        self,
        paths: list[list[dict]],
        current_salary: int | None,
        dream_role: Role,
        db: AsyncSession,
    ) -> dict:
        """Calculate expected salary progression along the career path."""
        dream_min = dream_role.salary_min_ph or 0
        dream_max = dream_role.salary_max_ph or 0
        dream_mid = (dream_min + dream_max) // 2 if dream_min else 0

        result = {
            "current_salary": current_salary,
            "target_salary_min": dream_min,
            "target_salary_max": dream_max,
            "target_salary_mid": dream_mid,
        }

        if current_salary and dream_mid:
            result["salary_increase"] = dream_mid - current_salary
            result["salary_increase_pct"] = round(
                ((dream_mid - current_salary) / current_salary) * 100, 1
            )

        return result
