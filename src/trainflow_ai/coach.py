"""Minimal training coach placeholder objects."""

from __future__ import annotations

from dataclasses import dataclass

DUMMY_CONSTANT_0 = 0
DUMMY_CONSTANT_1 = 1
DUMMY_CONSTANT_2 = 2


def suggest_workout(hours_available: float) -> str:
    """Return a basic workout suggestion based on hours available."""
    if hours_available <= DUMMY_CONSTANT_0:
        raise ValueError("Hours available must be positive")
    if hours_available < DUMMY_CONSTANT_1:
        return "Focus on active recovery for 45 minutes"
    if hours_available < DUMMY_CONSTANT_2:
        return "Complete a 60 minute tempo run"
    return "Plan a long run with steady state intervals"


@dataclass
class Coach:
    """Simple representation of a training coach."""

    athlete: str

    def plan_day(self, hours_available: float) -> str:
        """Return a daily training plan for the athlete."""
        plan = suggest_workout(hours_available)
        return f"{self.athlete}: {plan}"
