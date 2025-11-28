from __future__ import annotations

from pathlib import Path

import pytest

from trainflow_ai.zwo import (
    CooldownStep,
    FreeRideStep,
    RampStep,
    RestStep,
    SteadyStateStep,
    Target,
    TargetKind,
    WarmupStep,
    Workout,
    WorkoutFile,
    parse_zwo_file,
    workout_file_to_string,
)

SAMPLE_PROGRAM_1 = Path(__file__).parent / "sample_files" / "sample_program_1.zwo"
SAMPLE_PROGRAM_2 = Path(__file__).parent / "sample_files" / "sample_program_2.zwo"
SAMPLE_PROGRAM_3 = Path(__file__).parent / "sample_files" / "sample_program_3.zwo"
SAMPLE_PROGRAMS = [SAMPLE_PROGRAM_1, SAMPLE_PROGRAM_2, SAMPLE_PROGRAM_3]


@pytest.mark.parametrize("sample_path", SAMPLE_PROGRAMS)
def test_round_trip_serialization(tmp_path: Path, sample_path: Path) -> None:
    if sample_path.name == "sample_program_3.zwo":
        with pytest.raises(ValueError):
            parse_zwo_file(sample_path)
        return

    wf = parse_zwo_file(sample_path)
    xml = workout_file_to_string(wf)
    # Write and parse again to ensure it remains valid XML
    path = tmp_path / "roundtrip.zwo"
    path.write_text(xml, encoding="utf-8")
    wf2 = parse_zwo_file(path)
    assert wf2.name == wf.name
    assert len(wf2.workouts) == len(wf.workouts)


@pytest.mark.parametrize(
    "step",
    [
        WarmupStep(duration_seconds=60, target=Target(TargetKind.POWER, 0.5)),
        SteadyStateStep(duration_seconds=120, target=Target(TargetKind.PACE, 2.5)),
        CooldownStep(duration_seconds=30, target=Target(TargetKind.POWER, 150.0)),
        RestStep(duration_seconds=45, target=Target(TargetKind.POWER, 0.2)),
        FreeRideStep(duration_seconds=90),
        RampStep(
            duration_seconds=20,
            target_start=Target(TargetKind.POWER, 0.6),
            target_end=Target(TargetKind.POWER, 0.8),
        ),
    ],
)
def test_writer_emits_valid_xml_for_steps(step: WarmupStep) -> None:
    wf = WorkoutFile(
        author="tester",
        name="single",
        workouts=[Workout(name="wo", steps=[step])],
    )
    xml = workout_file_to_string(wf)
    assert "<workout_file>" in xml
    assert '<workout name="wo">' in xml


def test_writer_errors_on_mixed_ramp_targets(tmp_path: Path) -> None:
    bad_ramp = RampStep(
        duration_seconds=10,
        target_start=Target(TargetKind.POWER, 0.5),
        target_end=Target(TargetKind.PACE, 3.0),
    )
    wf = WorkoutFile(author=None, name="bad", workouts=[Workout(name="wo", steps=[bad_ramp])])
    with pytest.raises(ValueError):
        workout_file_to_string(wf)
