"""Utility for parsing Philippine peso salary strings into numeric values."""

import re


def parse_salary_range_ph(salary_str: str | None) -> tuple[int | None, int | None]:
    """Parse 'PHP 35,000 - 80,000' → (35000, 80000)."""
    if not salary_str:
        return None, None

    numbers = re.findall(r"[\d,]+", salary_str)
    if not numbers:
        return None, None

    parsed = [int(n.replace(",", "")) for n in numbers]

    if len(parsed) >= 2:
        return parsed[0], parsed[1]
    if len(parsed) == 1:
        return parsed[0], parsed[0]
    return None, None


def salary_midpoint(salary_str: str | None) -> int | None:
    """Get the midpoint of a salary range string."""
    low, high = parse_salary_range_ph(salary_str)
    if low is not None and high is not None:
        return (low + high) // 2
    return low or high


def format_php(amount: int | None) -> str:
    """Format an integer as 'PHP 35,000'."""
    if amount is None:
        return ""
    return f"PHP {amount:,}"
