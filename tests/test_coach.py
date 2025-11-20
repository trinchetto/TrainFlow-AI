from trainflow_ai import Coach
from trainflow_ai.coach import suggest_workout


def test_suggest_workout_ranges() -> None:
    assert "recovery" in suggest_workout(0.5)
    assert "tempo" in suggest_workout(1.5)
    assert "long run" in suggest_workout(3)


def test_coach_plan_day_message() -> None:
    plan = Coach("Alex").plan_day(1.25)
    assert plan.startswith("Alex:")
    assert "tempo" in plan
