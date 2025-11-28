"""Lightweight FIT writer wrapper using fit-tool."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, cast

from fit_tool.fit_file_builder import FitFileBuilder

from trainflow_ai.logging_utils import StructuredLogger

logger = StructuredLogger("trainflow_ai.fit.writer")


def _serialize_fit(messages: Iterable[Any]) -> bytes:
    message_list = list(messages)
    try:
        builder = FitFileBuilder(auto_define=True)
    except Exception:
        builder = FitFileBuilder()
    for msg in message_list:
        try:
            builder.add(msg)
        except Exception as exc:
            raise ValueError("Invalid FIT message provided to writer") from exc
    fit_obj = builder.build()
    if hasattr(fit_obj, "to_bytes"):
        to_bytes = cast(Any, fit_obj.to_bytes)
        return cast(bytes, to_bytes())
    if hasattr(fit_obj, "as_bytes"):
        as_bytes = cast(Any, fit_obj.as_bytes)
        return cast(bytes, as_bytes())
    if isinstance(fit_obj, (bytes, bytearray)):
        return bytes(fit_obj)
    raise ValueError("Unable to serialize FIT data with fit-tool builder")


@logger.with_error_handling(reraise=True)
def fit_file_to_bytes(messages: Iterable[Any]) -> bytes:
    """Encode fit-tool messages into FIT binary bytes."""
    message_list = list(messages)
    data = _serialize_fit(message_list)
    logger.debug("Encoded FIT messages", message_count=len(message_list))
    return data


@logger.with_error_handling(reraise=True)
def save_fit_file(messages: Iterable[Any], path: str | Path) -> Path:
    """Encode and save FIT data to disk."""
    message_list = list(messages)
    data = _serialize_fit(message_list)
    out_path = Path(path)
    out_path.write_bytes(data)
    logger.info("Saved FIT file", path=str(out_path), message_count=len(message_list))
    return out_path
