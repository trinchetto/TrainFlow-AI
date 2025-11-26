"""Parser for Zwift ZWO workout files into the lightweight data model."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, cast

from trainflow_ai.logging_utils import StructuredLogger
from trainflow_ai.zwo.zwo_model import (
    CooldownStep,
    FreeRideStep,
    RampStep,
    RepeatBlock,
    RestStep,
    SteadyStateStep,
    Step,
    Target,
    TargetKind,
    WarmupStep,
    Workout,
    WorkoutFile,
)

logger = StructuredLogger("trainflow_ai.zwo.parser")


def _parse_target(
    element: ET.Element, *, low_key: str | None = None, high_key: str | None = None
) -> Tuple[Target, Optional[Target]]:
    """
    Parse a single or double-ended target.
    - Uses Power*/Pace* attributes (case sensitive as per Zwift reference).
    - Falls back to lowercase pace if present.
    """
    units = element.get("units")

    def build(kind: TargetKind, val_str: str) -> Target:
        val = float(val_str)
        is_fraction = kind == TargetKind.POWER and val <= 1.0
        return Target(kind=kind, value=val, is_fraction_of_ftp=is_fraction, units=units)

    if low_key and high_key:
        low_val = element.get(low_key) or element.get(low_key.lower())
        high_val = element.get(high_key) or element.get(high_key.lower())
        if low_val is None or high_val is None:
            raise ValueError(
                f"Missing required attribute '{low_key}' or '{high_key}' on <{element.tag}>"
            )
        # Decide target type based on available attributes
        kind = TargetKind.POWER if ("Power" in low_key or "Power" in high_key) else TargetKind.PACE
        return build(kind, low_val), build(kind, high_val)

    # Single target
    power = element.get("Power")
    pace = element.get("Pace") or element.get("pace")
    if power is not None:
        return build(TargetKind.POWER, power), None
    if pace is not None:
        return build(TargetKind.PACE, pace), None

    raise ValueError(f"Missing target attribute on <{element.tag}>")


def _require_attr(element: ET.Element, attr: str) -> str:
    value = element.get(attr)
    if value is None:
        raise ValueError(f"Missing required attribute '{attr}' on <{element.tag}>")
    return value


def _parse_step(element: ET.Element) -> Step:
    tag = element.tag

    if tag == "Repeat":
        count = int(_require_attr(element, "Repeat"))
        steps: List[Step] = [_parse_step(child) for child in _child_elements(element)]
        return RepeatBlock(repeat_count=count, steps=steps)

    duration = int(_require_attr(element, "Duration"))
    cadence = element.get("Cadence")
    cadence_int = int(cadence) if cadence is not None else None
    text = element.get("Text")

    if tag in {"Warmup", "SteadyState", "Cooldown", "Rest"}:
        target, _ = _parse_target(element)
        step_cls = {
            "Warmup": WarmupStep,
            "SteadyState": SteadyStateStep,
            "Cooldown": CooldownStep,
            "Rest": RestStep,
        }[tag]
        return cast(
            Step,
            step_cls(duration_seconds=duration, cadence_rpm=cadence_int, text=text, target=target),
        )

    if tag == "Ramp":
        try:
            low, high = _parse_target(element, low_key="PowerLow", high_key="PowerHigh")
        except ValueError:
            low, high = _parse_target(element, low_key="PaceLow", high_key="PaceHigh")
        low_t = low
        high_t = cast(Target, high)
        return RampStep(
            duration_seconds=duration,
            cadence_rpm=cadence_int,
            text=text,
            target_start=low_t,
            target_end=high_t,
        )

    if tag in {"FreeRide", "Freeride"}:
        target_val: Optional[Target] = None
        if element.get("Power") or element.get("Pace") or element.get("pace"):
            target_val, _ = _parse_target(element)
        return FreeRideStep(
            duration_seconds=duration, cadence_rpm=cadence_int, text=text, target=target_val
        )

    raise ValueError(f"Unsupported step type <{tag}>")


def _child_elements(element: ET.Element) -> Iterable[ET.Element]:
    for child in element:
        if isinstance(child.tag, str):
            yield child


@logger.with_error_handling(reraise=True)
def parse_zwo_file(path: str | Path) -> WorkoutFile:
    """Parse a ZWO file into a WorkoutFile model."""
    raw = Path(path).read_text(encoding="utf-8")
    logger.debug("Parsing ZWO file", path=str(path))
    # Escape bare ampersands often found in real-world ZWO attribute values.
    sanitized = re.sub(r"&(?!(amp;|lt;|gt;|quot;|apos;))", "&amp;", raw)
    root = ET.fromstring(sanitized)
    if root.tag != "workout_file":
        raise ValueError("Root element must be <workout_file>")

    author = root.findtext("author")
    name = root.findtext("name") or "Untitled"
    description = root.findtext("description")
    sport_type = root.findtext("sportType") or "bike"

    tags_text = root.findtext("tags") or ""
    tags: List[str] = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

    workouts: List[Workout] = []
    for workout_el in root.findall("workout"):
        workout_name = workout_el.get("name") or "Untitled Workout"
        steps: List[Step] = [_parse_step(step_el) for step_el in _child_elements(workout_el)]
        workouts.append(Workout(name=workout_name, steps=steps))

    logger.info(
        "Parsed ZWO workout file",
        path=str(path),
        workouts=len(workouts),
        tags=len(tags),
    )
    return WorkoutFile(
        author=author,
        name=name,
        description=description,
        sport_type=sport_type,
        tags=tags,
        workouts=workouts,
    )
