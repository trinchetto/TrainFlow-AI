"""Writer for Zwift ZWO workout files from the lightweight data model."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

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

logger = StructuredLogger("trainflow_ai.zwo.writer")


def _target_attrs(target: Target) -> dict[str, str]:
    attrs: dict[str, str] = {}
    if target.kind == TargetKind.POWER:
        attrs["Power"] = str(target.value)
    elif target.kind == TargetKind.PACE:
        attrs["Pace"] = str(target.value)
    elif target.kind == TargetKind.HR:
        attrs["Power"] = str(
            target.value
        )  # Zwift doesn't have HR step attrs in common tags; reuse Power
    if target.units:
        attrs["units"] = target.units
    return attrs


def _step_to_element(step: Step) -> ET.Element:  # noqa: PLR0911, PLR0912
    if isinstance(step, RepeatBlock):
        repeat_el = ET.Element("Repeat", Repeat=str(step.repeat_count))
        for child in step.steps:
            repeat_el.append(_step_to_element(child))
        return repeat_el

    common_attrs = {"Duration": str(step.duration_seconds)}
    if step.cadence_rpm is not None:
        common_attrs["Cadence"] = str(step.cadence_rpm)
    if step.text:
        common_attrs["Text"] = step.text

    if isinstance(step, WarmupStep):
        attrs = {**common_attrs, **_target_attrs(step.target)}
        return ET.Element("Warmup", attrs)
    if isinstance(step, SteadyStateStep):
        attrs = {**common_attrs, **_target_attrs(step.target)}
        return ET.Element("SteadyState", attrs)
    if isinstance(step, CooldownStep):
        attrs = {**common_attrs, **_target_attrs(step.target)}
        return ET.Element("Cooldown", attrs)
    if isinstance(step, RestStep):
        attrs = {**common_attrs, **_target_attrs(step.target)}
        return ET.Element("Rest", attrs)
    if isinstance(step, RampStep):
        attrs = dict(common_attrs)
        if step.target_start.kind == step.target_end.kind == TargetKind.POWER:
            attrs["PowerLow"] = str(step.target_start.value)
            attrs["PowerHigh"] = str(step.target_end.value)
        elif step.target_start.kind == step.target_end.kind == TargetKind.PACE:
            attrs["PaceLow"] = str(step.target_start.value)
            attrs["PaceHigh"] = str(step.target_end.value)
        else:
            raise ValueError("Ramp targets must share kind (power or pace)")
        return ET.Element("Ramp", attrs)
    if isinstance(step, FreeRideStep):
        attrs = dict(common_attrs)
        if step.target:
            attrs.update(_target_attrs(step.target))
        return ET.Element("FreeRide", attrs)

    raise ValueError(f"Unsupported step type: {type(step)}")


def _workout_to_element(workout: Workout) -> ET.Element:
    workout_el = ET.Element("workout", {"name": workout.name})
    for step in workout.steps:
        workout_el.append(_step_to_element(step))
    return workout_el


def workout_file_to_element(workout_file: WorkoutFile) -> ET.Element:
    """Convert a WorkoutFile into the root XML element."""
    root = ET.Element("workout_file")
    if workout_file.author:
        ET.SubElement(root, "author").text = workout_file.author
    ET.SubElement(root, "name").text = workout_file.name
    if workout_file.description:
        ET.SubElement(root, "description").text = workout_file.description
    ET.SubElement(root, "sportType").text = workout_file.sport_type
    if workout_file.tags:
        ET.SubElement(root, "tags").text = ", ".join(workout_file.tags)

    for workout in workout_file.workouts:
        root.append(_workout_to_element(workout))
    return root


@logger.with_error_handling(reraise=True)
def workout_file_to_string(workout_file: WorkoutFile) -> str:
    """Serialize a WorkoutFile to a pretty-printed XML string."""
    logger.debug("Serializing workout file to XML", workouts=len(workout_file.workouts))
    root = workout_file_to_element(workout_file)
    return ET.tostring(root, encoding="unicode")


@logger.with_error_handling(reraise=True)
def save_workout_file(workout_file: WorkoutFile, path: str | Path) -> Path:
    """Save a WorkoutFile to disk as .zwo."""
    xml_str = workout_file_to_string(workout_file)
    p = Path(path)
    p.write_text(xml_str, encoding="utf-8")
    logger.info("Saved ZWO workout file", path=str(p))
    return p
