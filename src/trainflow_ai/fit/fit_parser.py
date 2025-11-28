"""Lightweight FIT parser wrapper using fit-tool."""

from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import matplotlib.pyplot as plt
import numpy as np
from fit_tool.fit_file import FitFile
from fit_tool.profile.messages.record_message import RecordMessage

from trainflow_ai.logging_utils import StructuredLogger

logger = StructuredLogger("trainflow_ai.fit.parser")


def _count_messages(fit_obj: Any) -> int:
    messages = getattr(fit_obj, "messages", None)
    if isinstance(messages, Iterable):
        try:
            return len(messages)  # type: ignore[arg-type]
        except Exception:
            return 0
    return 0


@logger.with_error_handling(reraise=True)
def parse_fit_file(path: str | Path) -> FitFile:
    """Parse a FIT file and return the fit-tool FitFile (or equivalent) object."""
    fit_path = Path(path)
    logger.debug("Parsing FIT file", path=str(fit_path))

    if hasattr(FitFile, "from_file"):
        fit_obj = FitFile.from_file(str(fit_path))
    else:
        fit_obj = FitFile(str(fit_path))

    if hasattr(fit_obj, "parse"):
        fit_obj.parse()

    logger.info(
        "Parsed FIT file successfully",
        path=str(fit_path),
        messages=_count_messages(fit_obj),
    )
    return fit_obj


def main() -> None:  # noqa: PLR0912, PLR0915
    """Parse the repository's sample FIT file for quick local testing."""
    sample_fit = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "tests"
        / "sample_files"
        / "sample_recording_3.FIT"
    )

    if not sample_fit.exists():
        raise FileNotFoundError(f"Sample FIT file not found at {sample_fit}")

    logger.info("Running sample FIT parse", path=str(sample_fit))
    fit_obj = parse_fit_file(sample_fit)

    # Collect every field that contains a value (keyed by field name).
    field_data: dict[str, list[tuple[float, Any]]] = defaultdict(list)
    saw_timestamp = False
    record_index = 0

    for record in getattr(fit_obj, "records", []):
        message = getattr(record, "message", None)
        if not isinstance(message, RecordMessage):
            continue
        record_index += 1

        record_timestamp: float | None = None
        for field in message.fields:
            if field.name == "timestamp":
                try:
                    record_timestamp = float(field.get_value())
                    saw_timestamp = True
                except Exception:
                    record_timestamp = None
                break

        if record_timestamp is None:
            record_timestamp = float(record_index)

        for field in message.fields:
            try:
                value = field.get_value()
            except Exception:
                continue
            if value is None:
                continue
            field_data[field.name].append((record_timestamp, value))

    if not field_data:
        logger.warning("No fields with data found in FIT file")
        return

    print("Fields present with data:")
    for name in sorted(field_data.keys()):
        print(f"- {name} ({len(field_data[name])} points)")

    numeric_types = (int, float, np.integer, np.floating)
    numeric_fields = {
        name: points
        for name, points in field_data.items()
        if all(isinstance(value, numeric_types) for _, value in points)
    }

    if not numeric_fields:
        logger.warning("No numeric fields available to plot")
        return

    base_timestamp = min(ts for points in numeric_fields.values() for ts, _ in points)

    def normalize_time(ts: float) -> float:
        if saw_timestamp:
            return (ts - base_timestamp) / 1000.0
        return ts - base_timestamp

    numeric_field_items = [(name, numeric_fields[name]) for name in sorted(numeric_fields)]
    num_fields = len(numeric_field_items)
    cols = 2 if num_fields > 1 else 1
    rows = math.ceil(num_fields / cols)
    fig, axes = plt.subplots(rows, cols, sharex=True, figsize=(10, max(4, 2 * rows)))
    axes = np.atleast_1d(axes).ravel()

    for ax, (name, points) in zip(axes, numeric_field_items, strict=False):
        times = np.array([normalize_time(ts) for ts, _ in points], dtype=float)
        values = np.array([float(value) for _, value in points], dtype=float)
        ax.plot(times, values, "-o", markersize=2, label=name)
        ax.set_ylabel(name)
        ax.legend(loc="best")

    for ax in axes[num_fields:]:
        ax.remove()

    for ax in axes[:num_fields]:
        ax.set_xlabel("Time (s)" if saw_timestamp else "Record index")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
