from __future__ import annotations

from pathlib import Path
from typing import Type

import pytest

from trainflow_ai.zwo import (
    CooldownStep,
    FreeRideStep,
    RampStep,
    RepeatBlock,
    RestStep,
    SteadyStateStep,
    TargetKind,
    WarmupStep,
    parse_zwo_file,
)

SAMPLE_PATH = Path(__file__).parent / "sample_files" / "sample_program.zwo"


@pytest.mark.parametrize(  # type: ignore[misc]
    ("workout_index", "expected_name", "expected_step_types"),
    [
        (
            0,
            "Lunedì – Recupero e mobilità (30’)",
            [WarmupStep, SteadyStateStep, CooldownStep],
        ),
        (
            1,
            "Martedì – Torque + Sprint (Forza & Esplosività)",
            [WarmupStep, RepeatBlock, RepeatBlock, CooldownStep],
        ),
        (
            3,
            "Giovedì – VO2max 40/20 (Alta Intensità)",
            [WarmupStep, RepeatBlock, CooldownStep],
        ),
    ],
)
def test_parse_sample_workouts_nominal(
    workout_index: int, expected_name: str, expected_step_types: list[Type[object]]
) -> None:
    wf = parse_zwo_file(SAMPLE_PATH)

    workout = wf.workouts[workout_index]
    assert workout.name == expected_name
    assert [type(step) for step in workout.steps] == expected_step_types


def test_parse_sample_nested_repeat_and_ramp() -> None:
    wf = parse_zwo_file(SAMPLE_PATH)
    tuesday = wf.workouts[1]

    # First repeat block: torque efforts
    torque_block = tuesday.steps[1]
    assert isinstance(torque_block, RepeatBlock)
    assert torque_block.repeat_count == 3  # noqa: PLR2004
    assert [type(s) for s in torque_block.steps] == [SteadyStateStep, RestStep]
    assert isinstance(torque_block.steps[0], SteadyStateStep)
    assert torque_block.steps[0].cadence_rpm == 55  # noqa: PLR2004

    # Second repeat block: sprints with ramp
    sprint_block = tuesday.steps[2]
    assert isinstance(sprint_block, RepeatBlock)
    assert sprint_block.repeat_count == 6  # noqa: PLR2004
    assert [type(s) for s in sprint_block.steps] == [RampStep, RestStep]
    ramp = sprint_block.steps[0]
    assert isinstance(ramp, RampStep)
    assert ramp.target_start.kind == TargetKind.POWER
    assert ramp.target_start.value == 363  # noqa: PLR2004
    assert ramp.target_end.value == 495  # noqa: PLR2004


@pytest.mark.parametrize(  # type: ignore[misc]
    "bad_xml",
    [
        "<workout_file><workout><SteadyState Power='200'/></workout></workout_file>",  # missing Duration
        "<workout_file><workout><Unknown Duration='60' Power='100'/></workout></workout_file>",
        "<badroot></badroot>",
    ],
)
def test_parse_errors(bad_xml: str, tmp_path: Path) -> None:
    path = tmp_path / "bad.zwo"
    path.write_text(bad_xml)
    with pytest.raises(ValueError):
        parse_zwo_file(path)


def test_parse_pace_targets_and_free_ride(tmp_path: Path) -> None:
    xml = """
    <workout_file>
      <name>Pace test</name>
      <workout>
        <SteadyState Duration="300" Pace="2.5" />
        <Ramp Duration="100" PaceLow="2.5" PaceHigh="3.0" />
        <FreeRide Duration="200" />
      </workout>
    </workout_file>
    """
    path = tmp_path / "pace.zwo"
    path.write_text(xml)

    wf = parse_zwo_file(path)
    steps = wf.workouts[0].steps

    steady = steps[0]
    assert isinstance(steady, SteadyStateStep)
    assert steady.target.kind == TargetKind.PACE
    assert steady.target.value == 2.5  # noqa: PLR2004

    ramp = steps[1]
    assert isinstance(ramp, RampStep)
    assert ramp.target_start.kind == TargetKind.PACE
    assert ramp.target_end.value == 3.0  # noqa: PLR2004

    free = steps[2]
    assert isinstance(free, FreeRideStep)
    assert free.target is None
