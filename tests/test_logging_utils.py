from __future__ import annotations

import asyncio
import io
import json
import logging

from trainflow_ai.logging_utils import (
    StructuredFormatter,
    StructuredLogger,
    set_correlation_id,
    set_user_session_id,
)


def _capture_log_output(logger: StructuredLogger) -> io.StringIO:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(StructuredFormatter())
    logger.handlers = [handler]  # replace handlers for test capture
    return stream


def test_structured_logger_outputs_json() -> None:
    """Ensure the logger emits Cloud Run style JSON with context fields."""
    logger = StructuredLogger("trainflow_ai.test", "DEBUG")
    stream = _capture_log_output(logger)

    set_correlation_id("req-123")
    set_user_session_id("sess-456")

    logger.info("hello world", extra_field="value")

    data = json.loads(stream.getvalue().strip())

    assert data["message"] == "hello world"
    assert data["severity"] == "INFO"
    assert data["extra_field"] == "value"
    assert data["correlation_id"] == "req-123"
    assert data["user_session_id"] == "sess-456"
    assert "serviceContext" in data


def test_structured_logger_handles_exceptions() -> None:
    """Verify exceptions are embedded in the structured payload."""
    logger = StructuredLogger("trainflow_ai.test", "INFO")
    stream = _capture_log_output(logger)

    try:
        raise ValueError("boom")
    except ValueError as exc:
        logger.error("something failed", exc_info=exc, request_id="req-1")

    data = json.loads(stream.getvalue().strip())

    assert data["severity"] == "ERROR"
    assert data["request_id"] == "req-1"
    assert data["error"]["type"] == "ValueError"
    assert "boom" in data["error"]["message"]


def test_with_error_handling_sync() -> None:
    """Decorator should swallow errors and return the fallback response."""
    logger = StructuredLogger("trainflow_ai.test", "INFO")

    @logger.with_error_handling(fallback_response="fallback")
    def boom() -> str:
        raise RuntimeError("oops")

    assert boom() == "fallback"


def test_with_error_handling_async() -> None:
    """Async functions are wrapped with the same structured handling."""
    logger = StructuredLogger("trainflow_ai.test", "INFO")

    @logger.with_error_handling(fallback_response="async-fallback")
    async def async_boom() -> str:
        raise RuntimeError("oops")

    assert asyncio.run(async_boom()) == "async-fallback"
