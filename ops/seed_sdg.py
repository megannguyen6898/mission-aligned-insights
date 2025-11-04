from __future__ import annotations

from typing import Iterable

from backend.app.database import SessionLocal
from backend.app.models import SDGGoal, SDGTarget, SDGIndicator


SDG_DATA: Iterable[dict] = [
    {
        "number": 1,
        "title": "No Poverty",
        "short_title": "No Poverty",
        "description": "End poverty in all its forms everywhere.",
        "color": "#e5243b",
        "targets": [
            {
                "code": "1.1",
                "title": "Eradicate extreme poverty",
                "description": "By 2030, eradicate extreme poverty for all people everywhere.",
                "indicators": [
                    {
                        "code": "1.1.1",
                        "title": "Proportion of population below the international poverty line",
                        "description": "Share of population living below $1.90/day.",
                    }
                ],
            },
            {
                "code": "1.2",
                "title": "Reduce poverty in all dimensions",
                "description": "Reduce by at least half the proportion of people living in poverty.",
                "indicators": [
                    {
                        "code": "1.2.1",
                        "title": "Proportion of population living below the national poverty line",
                        "description": "Share of population living below the national poverty line.",
                    },
                    {
                        "code": "1.2.2",
                        "title": "Proportion of men, women and children living in poverty",
                        "description": "Multidimensional poverty index score for total population.",
                    },
                ],
            },
        ],
    },
    {
        "number": 3,
        "title": "Good Health and Well-being",
        "short_title": "Good Health",
        "description": "Ensure healthy lives and promote well-being for all at all ages.",
        "color": "#4c9f38",
        "targets": [
            {
                "code": "3.1",
                "title": "Maternal health",
                "description": "Reduce the global maternal mortality ratio.",
                "indicators": [
                    {
                        "code": "3.1.1",
                        "title": "Maternal mortality ratio",
                        "description": "Number of maternal deaths per 100,000 live births.",
                    }
                ],
            },
            {
                "code": "3.3",
                "title": "Communicable diseases",
                "description": "End epidemics of major communicable diseases.",
                "indicators": [
                    {
                        "code": "3.3.1",
                        "title": "Incidence of HIV infection per 1,000 uninfected population",
                        "description": "Annual number of new HIV infections per 1,000 uninfected population.",
                    },
                    {
                        "code": "3.3.2",
                        "title": "Tuberculosis incidence per 100,000 population",
                        "description": "Number of new TB cases per 100,000 population.",
                    },
                ],
            },
        ],
    },
    {
        "number": 4,
        "title": "Quality Education",
        "short_title": "Quality Education",
        "description": "Ensure inclusive and equitable quality education and promote lifelong learning.",
        "color": "#c5192d",
        "targets": [
            {
                "code": "4.1",
                "title": "Completion rates",
                "description": "Ensure that all girls and boys complete free, equitable and quality primary and secondary education.",
                "indicators": [
                    {
                        "code": "4.1.1",
                        "title": "Completion rate (primary education)",
                        "description": "Percentage of children completing primary education.",
                    },
                    {
                        "code": "4.1.2",
                        "title": "Completion rate (lower secondary education)",
                        "description": "Percentage of children completing lower secondary education.",
                    },
                ],
            },
            {
                "code": "4.4",
                "title": "Skills for employment",
                "description": "Increase the number of people with relevant skills for employment, decent jobs and entrepreneurship.",
                "indicators": [
                    {
                        "code": "4.4.1",
                        "title": "Proportion of youth with ICT skills",
                        "description": "Share of youth and adults with ICT skills.",
                    }
                ],
            },
        ],
    },
]


def seed_sdg() -> None:
    session = SessionLocal()
    try:
        for goal_data in SDG_DATA:
            goal = session.query(SDGGoal).filter(SDGGoal.number == goal_data["number"]).first()
            if not goal:
                goal = SDGGoal(
                    number=goal_data["number"],
                    title=goal_data["title"],
                    short_title=goal_data.get("short_title"),
                    description=goal_data.get("description"),
                    color=goal_data.get("color"),
                )
                session.add(goal)
                session.flush()
            else:
                goal.title = goal_data["title"]
                goal.short_title = goal_data.get("short_title")
                goal.description = goal_data.get("description")
                goal.color = goal_data.get("color")

            for target_data in goal_data.get("targets", []):
                target = session.query(SDGTarget).filter(SDGTarget.code == target_data["code"]).first()
                if not target:
                    target = SDGTarget(
                        goal_id=goal.id,
                        code=target_data["code"],
                        title=target_data["title"],
                        description=target_data.get("description"),
                    )
                    session.add(target)
                    session.flush()
                else:
                    target.goal_id = goal.id
                    target.title = target_data["title"]
                    target.description = target_data.get("description")

                for indicator_data in target_data.get("indicators", []):
                    indicator = (
                        session.query(SDGIndicator)
                        .filter(SDGIndicator.code == indicator_data["code"])
                        .first()
                    )
                    if not indicator:
                        indicator = SDGIndicator(
                            target_id=target.id,
                            code=indicator_data["code"],
                            title=indicator_data["title"],
                            description=indicator_data.get("description"),
                        )
                        session.add(indicator)
                    else:
                        indicator.target_id = target.id
                        indicator.title = indicator_data["title"]
                        indicator.description = indicator_data.get("description")
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    seed_sdg()
