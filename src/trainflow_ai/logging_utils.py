"""Structured, Cloud Run-friendly logging utilities built around a class API."""

from __future__ import annotations

import inspect
import json
import logging
import os
import sys
import time
import traceback
from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps
from types import TracebackType
from typing import Any, Callable, Dict, Mapping, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

# Context variables for request correlation
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
user_session_id: ContextVar[Optional[str]] = ContextVar("user_session_id", default=None)

ExcInfoTuple = tuple[type[BaseException], BaseException, TracebackType | None]
ExcInfoOrNoneTuple = ExcInfoTuple | tuple[None, None, None]


def set_correlation_id(cid: str) -> None:
    """Set correlation ID for request tracing."""
    correlation_id.set(cid)


def set_user_session_id(uid: str) -> None:
    """Set user session ID for request tracing."""
    user_session_id.set(uid)


class StructuredFormatter(logging.Formatter):
    """Cloud Run compatible JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - exercised indirectly
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        func_name = record.funcName or "<unknown>"

        log_entry: Dict[str, Any] = {
            "timestamp": timestamp,
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": func_name,
            "line": record.lineno,
            "logging.googleapis.com/sourceLocation": {
                "file": record.pathname,
                "line": record.lineno,
                "function": func_name,
            },
        }

        # Add correlation IDs if available
        if correlation_id.get():
            log_entry["correlation_id"] = correlation_id.get()
        if user_session_id.get():
            log_entry["user_session_id"] = user_session_id.get()

        # Cloud Run service metadata
        service_name = os.getenv("K_SERVICE") or os.getenv("CLOUD_RUN_SERVICE") or "trainflow-ai"
        service_revision = os.getenv("K_REVISION")
        log_entry["serviceContext"] = {"service": service_name}
        if service_revision:
            log_entry["serviceContext"]["version"] = service_revision

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_entry.update(getattr(record, "extra_fields", {}))

        # Add exception info if present
        if record.exc_info:
            log_entry["error"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        return json.dumps(log_entry)


class StructuredLogger(logging.Logger):
    """Cloud Run-friendly structured logger with built-in error handling."""

    _configured = False

    def __init__(self, name: str = "trainflow_ai", level: str | None = None) -> None:
        configured_level = level or os.getenv("LOG_LEVEL", "INFO") or "INFO"
        self._configure_root(configured_level)
        numeric_level = getattr(logging, configured_level.upper(), logging.INFO)
        super().__init__(name, numeric_level)
        if level:
            self.setLevel(getattr(logging, level.upper(), logging.INFO))
        # Ensure records propagate to the configured root handlers
        self.parent = logging.getLogger()
        self.propagate = True

    @classmethod
    def _configure_root(cls, level: str) -> None:
        if cls._configured:
            return
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(handler)
        root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        cls._configured = True

    def _structured_log(  # noqa: PLR0913 - keeping signature aligned with logging.Logger
        self,
        level: int,
        msg: object,
        *args: object,
        exc_info: BaseException | bool | ExcInfoOrNoneTuple | None = None,
        stack_info: bool = False,
        stacklevel: int = 2,
        extra: Mapping[str, object] | None = None,
        **extra_fields: object,
    ) -> None:
        merged_fields: Dict[str, object] = {**extra_fields}
        if extra:
            merged_fields.update(extra)

        super().log(
            level,
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra={"extra_fields": merged_fields},
        )

    def debug(
        self,
        msg: object,
        *args: object,
        exc_info: BaseException | bool | ExcInfoOrNoneTuple | None = None,
        stack_info: bool = False,
        stacklevel: int = 2,
        extra: Mapping[str, object] | None = None,
        **extra_fields: object,
    ) -> None:
        self._structured_log(
            logging.DEBUG,
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
            **extra_fields,
        )

    def info(
        self,
        msg: object,
        *args: object,
        exc_info: BaseException | bool | ExcInfoOrNoneTuple | None = None,
        stack_info: bool = False,
        stacklevel: int = 2,
        extra: Mapping[str, object] | None = None,
        **extra_fields: object,
    ) -> None:
        self._structured_log(
            logging.INFO,
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
            **extra_fields,
        )

    def warning(
        self,
        msg: object,
        *args: object,
        exc_info: BaseException | bool | ExcInfoOrNoneTuple | None = None,
        stack_info: bool = False,
        stacklevel: int = 2,
        extra: Mapping[str, object] | None = None,
        **extra_fields: object,
    ) -> None:
        self._structured_log(
            logging.WARNING,
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
            **extra_fields,
        )

    def error(
        self,
        msg: object,
        *args: object,
        exc_info: BaseException | bool | ExcInfoOrNoneTuple | None = None,
        stack_info: bool = False,
        stacklevel: int = 2,
        extra: Mapping[str, object] | None = None,
        **extra_fields: object,
    ) -> None:
        self._structured_log(
            logging.ERROR,
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
            **extra_fields,
        )

    def with_error_handling(
        self,
        fallback_response: Any = None,
        reraise: bool = False,
    ) -> Callable[[F], F]:
        """Decorator wrapping sync/async callables with structured error logging."""

        def decorator(func: F) -> F:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                self.debug(
                    f"Entering {func.__name__}",
                    function=func.__name__,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys()),
                )

                start_time = time.time()

                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.info(
                        f"Successfully completed {func.__name__}",
                        function=func.__name__,
                        duration_seconds=round(duration, 3),
                        success=True,
                    )
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.error(
                        f"Error in {func.__name__}: {str(e)}",
                        function=func.__name__,
                        duration_seconds=round(duration, 3),
                        success=False,
                        error_type=type(e).__name__,
                        error_message=str(e),
                        exc_info=e,
                    )
                    if reraise:
                        raise
                    return fallback_response

            if inspect.iscoroutinefunction(func):

                @wraps(func)
                async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    self.debug(
                        f"Entering async {func.__name__}",
                        function=func.__name__,
                        args_count=len(args),
                        kwargs_keys=list(kwargs.keys()),
                    )

                    start_time = time.time()

                    try:
                        result = await func(*args, **kwargs)
                        duration = time.time() - start_time
                        self.info(
                            f"Successfully completed async {func.__name__}",
                            function=func.__name__,
                            duration_seconds=round(duration, 3),
                            success=True,
                        )
                        return result
                    except Exception as e:
                        duration = time.time() - start_time
                        self.error(
                            f"Error in async {func.__name__}: {str(e)}",
                            function=func.__name__,
                            duration_seconds=round(duration, 3),
                            success=False,
                            error_type=type(e).__name__,
                            error_message=str(e),
                            exc_info=e,
                        )
                        if reraise:
                            raise
                        return fallback_response

                return async_wrapper  # type: ignore

            return wrapper  # type: ignore

        return decorator
