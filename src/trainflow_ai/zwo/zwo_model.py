"""Lightweight data model for Zwift ZWO workout files.

The ZWO format is an XML structure that defines structured workouts:
metadata (author, name, description, sportType, tags) and one or more
`<workout>` blocks containing time-based steps (warmup, steady, rest,
ramp) plus repeat groups. This model is intentionally small and covers
the constructs seen in the reference examples (see tests/sample_files/sample_program.zwo).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Union


class TargetKind(str, Enum):
    POWER = "power"
    PACE = "pace"
    HR = "hr"


@dataclass
class Target:
    """Numeric target with a type identifier (power, pace, hr, etc.)."""

    kind: TargetKind
    value: float
    is_fraction_of_ftp: bool = False  # used for power targets
    units: Optional[str] = None  # optional free-form units (e.g., "m/s")


@dataclass
class BaseStep:
    """Common fields shared by all time-based steps."""

    duration_seconds: int
    cadence_rpm: Optional[int] = None
    text: Optional[str] = None  # ZWO supports free text overlays


@dataclass
class WarmupStep(BaseStep):
    target: Target = field(default_factory=lambda: Target(TargetKind.POWER, 0.0))


@dataclass
class SteadyStateStep(BaseStep):
    target: Target = field(default_factory=lambda: Target(TargetKind.POWER, 0.0))


@dataclass
class CooldownStep(BaseStep):
    target: Target = field(default_factory=lambda: Target(TargetKind.POWER, 0.0))


@dataclass
class RestStep(BaseStep):
    target: Target = field(default_factory=lambda: Target(TargetKind.POWER, 0.0))


@dataclass
class RampStep(BaseStep):
    target_start: Target = field(default_factory=lambda: Target(TargetKind.POWER, 0.0))
    target_end: Target = field(default_factory=lambda: Target(TargetKind.POWER, 0.0))


@dataclass
class FreeRideStep(BaseStep):
    """Free-ride block with optional target/cadence hints."""

    target: Optional[Target] = None


@dataclass
class RepeatBlock:
    """A repeat wrapper that nests one or more steps."""

    repeat_count: int
    steps: List["Step"]


Step = Union[
    WarmupStep,
    SteadyStateStep,
    CooldownStep,
    RestStep,
    RampStep,
    FreeRideStep,
    RepeatBlock,
]


@dataclass
class Workout:
    """Single workout inside a workout_file."""

    name: str
    steps: List[Step]


@dataclass
class WorkoutFile:
    """Top-level structure for a ZWO file."""

    author: Optional[str]
    name: str
    description: Optional[str] = None
    sport_type: str = "bike"
    tags: List[str] = field(default_factory=list)
    workouts: List[Workout] = field(default_factory=list)
