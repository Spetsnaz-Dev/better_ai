"""
Shared constants used across the application.
Single source of truth — import from here instead of hardcoding values.
"""

# AI classification categories (Section 6 of AGENTS.md)
ALLOWED_CATEGORIES = {'WORK', 'PERSONAL', 'FINANCE', 'HEALTH', 'OTHER'}

# Fallback category when AI fails or returns invalid value
FALLBACK_CATEGORY = 'OTHER'


class TaskStatus:
    """Task status enum values."""
    PENDING = 'PENDING'
    PROCESSED = 'PROCESSED'
