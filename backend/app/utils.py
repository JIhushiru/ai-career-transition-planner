"""Shared utility functions."""

import json
import logging

logger = logging.getLogger(__name__)


def safe_json_loads(value: str | None, default: list | dict | None = None) -> list | dict:
    """Parse JSON string safely, returning default on failure."""
    if default is None:
        default = []
    if not value:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        logger.warning("Failed to parse JSON: %s", value[:100] if value else "")
        return default
