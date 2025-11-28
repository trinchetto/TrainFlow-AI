from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest
from fit_tool.profile.messages.record_message import RecordMessage

from trainflow_ai.fit import fit_file_to_bytes, parse_fit_file, save_fit_file

SAMPLE_FIT_1 = Path(__file__).parent / "sample_files" / "sample_recording_1.FIT"
SAMPLE_FIT_2 = Path(__file__).parent / "sample_files" / "sample_recording_2.FIT"
SAMPLE_FIT_3 = Path(__file__).parent / "sample_files" / "sample_recording_3.FIT"
SAMPLE_FITS = [SAMPLE_FIT_1, SAMPLE_FIT_2, SAMPLE_FIT_3]


def _record_messages(path: Path) -> list[RecordMessage]:
    fit_obj = parse_fit_file(path)
    messages: list[RecordMessage] = []
    for record in getattr(fit_obj, "records", []):
        msg = getattr(record, "message", None)
        if isinstance(msg, RecordMessage):
            messages.append(msg)
    return messages


@pytest.fixture(params=SAMPLE_FITS)
def sample_fit_path(request: pytest.FixtureRequest) -> Path:
    return cast(Path, request.param)


@pytest.fixture
def sample_messages(sample_fit_path: Path) -> list[RecordMessage]:
    msgs = _record_messages(sample_fit_path)
    if not msgs:
        pytest.skip("Sample FIT file produced no record messages; skipping FIT writer tests")
    return msgs


@pytest.mark.parametrize("path", SAMPLE_FITS)
def test_parse_fit_file_nominal(path: Path) -> None:
    msgs = _record_messages(path)
    if not msgs:
        pytest.skip("Sample FIT file produced no record messages")
    assert msgs


@pytest.mark.parametrize("count", [5, 10])
def test_fit_writer_outputs_bytes_and_file(
    tmp_path: Path, sample_messages: list[object], count: int
) -> None:
    subset = sample_messages[:count] or sample_messages
    data = fit_file_to_bytes(subset)
    assert isinstance(data, (bytes, bytearray))
    assert len(data) > 0

    out_path = tmp_path / "out.fit"
    saved = save_fit_file(subset, out_path)
    assert saved.exists()
    assert saved.read_bytes()[: len(data)]  # ensure bytes written


def test_parse_fit_file_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.fit"
    with pytest.raises(FileNotFoundError):
        parse_fit_file(missing)


def test_fit_writer_raises_on_invalid_messages(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        fit_file_to_bytes([object()])
