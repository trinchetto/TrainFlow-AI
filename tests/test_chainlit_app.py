from __future__ import annotations

import asyncio
import sys
from importlib import util
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Awaitable, Callable, Dict, cast

import pytest

from trainflow_ai.coach_graph import CoachState as CoachStateType


class _FakeUserSession(dict[str, Any]):
    def get(self, key: str, default: Any | None = None) -> Any:
        return super().get(key, default)

    def set(self, key: str, value: Any) -> None:
        self[key] = value


class _FakeChainlitModule(ModuleType):
    def __init__(self) -> None:
        super().__init__("chainlit")
        self.user_session = _FakeUserSession()
        self.make_async = lambda fn: fn

    @staticmethod
    def on_chat_start(func: Callable[..., Awaitable[None]]) -> Callable[..., Awaitable[None]]:
        return func

    @staticmethod
    def on_message(func: Callable[..., Awaitable[None]]) -> Callable[..., Awaitable[None]]:
        return func

    class Message:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.content = args[0] if args else kwargs.get("content")

        async def send(self) -> None:
            return None


def _load_chainlit_app() -> ModuleType:
    module_name = "chainlit_app"
    if module_name in sys.modules:
        return sys.modules[module_name]
    sys.modules.setdefault("chainlit", _FakeChainlitModule())
    module_path = Path(__file__).resolve().parents[1] / "src" / "trainflow_ai" / "chainlit_app.py"
    spec = util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load chainlit_app module")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


app = cast(Any, _load_chainlit_app())


class DummyChunk:
    def __init__(self, text: str | None):
        self.text = text


class DummyMessage:
    def __init__(self, content: Any):
        self.content = content


_fallback_obj = object()


@pytest.mark.parametrize(  # type: ignore[misc]
    ("message", "expected"),
    [
        ("simple", "simple"),
        (DummyMessage("attr str"), "attr str"),
        (DummyMessage([{"type": "text", "text": "A"}, {"type": "text", "text": "B"}]), "AB"),
        (DummyMessage([DummyChunk("hello"), DummyChunk(" world")]), "hello world"),
        (_fallback_obj, str(_fallback_obj)),
    ],
)
def test_serialize_response_variants(message: Any, expected: str) -> None:
    """Check the response serializer handles strings, dict chunks, and objects."""
    actual = app._serialize_response(message)
    assert actual == expected


def test_openai_llm_uses_chatopenai(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify the OpenAI-backed LLM formats prompts and returns serialized text."""
    captured: Dict[str, Any] = {}

    class FakeChat:
        def __init__(self, model: str, temperature: float) -> None:
            captured["model"] = model
            captured["temperature"] = temperature

        def invoke(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "raw-response"

    monkeypatch.setattr(app, "ChatOpenAI", FakeChat)
    monkeypatch.setattr(app, "_serialize_response", lambda message: f"serialized:{message}")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test")
    monkeypatch.setenv("OPENAI_TEMPERATURE", "0.75")

    llm = app._openai_llm()
    result = llm("Give me a plan")

    assert result == "serialized:raw-response"
    assert captured == {"model": "gpt-test", "temperature": 0.75, "prompt": "Give me a plan"}


def test_fallback_llm_returns_prompt() -> None:
    """Ensure the fallback LLM echoes the user's prompt in a canned response."""
    llm = app._fallback_llm()
    reply = llm("Just do it")
    assert "Just do it" in reply
    assert "Fallback" in reply


def test_build_llm_callable_prefers_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    """Confirm that presence of an API key uses the OpenAI client path."""
    sentinel = object()
    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    monkeypatch.setattr(app, "_openai_llm", lambda: sentinel)

    result = app._build_llm_callable()

    assert result is sentinel


def test_build_llm_callable_falls_back(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Check lack of API key falls back with an appropriate warning."""
    sentinel = object()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(app, "_fallback_llm", lambda: sentinel)

    with caplog.at_level("WARNING"):
        result = app._build_llm_callable()

    assert result is sentinel
    assert "OPENAI_API_KEY not set" in caplog.text


def test_build_runner_wires_graph(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the runner wraps a graph built with the selected LLM."""
    fake_runner = object()
    captured: Dict[str, Any] = {}

    def fake_build_graph(llm: Any) -> Any:
        captured["llm"] = llm
        return SimpleNamespace(invoke=lambda state: {"response": state["question"]})

    monkeypatch.setattr(app, "_build_llm_callable", lambda: "llm")
    monkeypatch.setattr(app, "build_coach_graph", fake_build_graph)
    monkeypatch.setattr(app.cl, "make_async", lambda fn: fake_runner)

    result = app._build_runner()

    assert result is fake_runner
    assert captured["llm"] == "llm"


class FakeSession(dict[str, Any]):
    def set(self, key: str, value: Any) -> None:
        self[key] = value


def test_get_runner_initializes_session(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify the Chainlit session stores a runner and reuses it."""
    session = FakeSession()
    monkeypatch.setattr(app.cl, "user_session", session)
    monkeypatch.setattr(app, "_build_runner", lambda: "runner1")

    result_first = app._get_runner()
    assert result_first == "runner1"
    assert session["graph_runner"] == "runner1"

    monkeypatch.setattr(app, "_build_runner", lambda: "runner2")
    result_second = app._get_runner()
    assert result_second == "runner1"


class FakeCLMessage:
    sent: list[str] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if args:
            self.content = args[0]
        else:
            self.content = kwargs.get("content")

    async def send(self) -> None:
        self.__class__.sent.append(self.content)


def test_on_chat_start_builds_runner(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure chat start creates a runner and sends the welcome message."""
    session = FakeSession()
    FakeCLMessage.sent = []
    monkeypatch.setattr(app.cl, "user_session", session)
    monkeypatch.setattr(app.cl, "Message", FakeCLMessage)
    monkeypatch.setattr(app, "_build_runner", lambda: "runner")

    asyncio.run(app.on_chat_start())

    assert session["graph_runner"] == "runner"
    assert FakeCLMessage.sent == [
        "Hi! Tell me how much time you have and how you're feeling, and I'll craft a training plan."
    ]


def test_on_message_uses_runner(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validate user prompts flow through the runner and responses reach the UI."""
    FakeCLMessage.sent = []
    monkeypatch.setattr(app.cl, "Message", FakeCLMessage)
    captured_state: list[CoachStateType] = []

    async def fake_runner(state: CoachStateType) -> CoachStateType:
        captured_state.append(state)
        return {"response": "Here you go"}

    monkeypatch.setattr(app, "_get_runner", lambda: fake_runner)

    incoming = SimpleNamespace(content="Need advice")

    asyncio.run(app.on_message(incoming))

    assert captured_state == [{"question": "Need advice"}]
    assert FakeCLMessage.sent == ["Here you go"]


def test_on_message_handles_missing_response(monkeypatch: pytest.MonkeyPatch) -> None:
    """Check empty runner output results in the fallback warning to the user."""
    FakeCLMessage.sent = []
    monkeypatch.setattr(app.cl, "Message", FakeCLMessage)

    async def fake_runner(state: CoachStateType) -> CoachStateType:
        return {}

    monkeypatch.setattr(app, "_get_runner", lambda: fake_runner)

    asyncio.run(app.on_message(SimpleNamespace(content="question")))

    assert FakeCLMessage.sent == ["I could not generate a response, please try again."]


def test_on_message_propagates_runner_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure exceptions from the runner are surfaced for upstream handling."""
    FakeCLMessage.sent = []
    monkeypatch.setattr(app.cl, "Message", FakeCLMessage)

    async def fake_runner(_: CoachStateType) -> CoachStateType:
        raise RuntimeError("boom")

    monkeypatch.setattr(app, "_get_runner", lambda: fake_runner)

    with pytest.raises(RuntimeError):
        asyncio.run(app.on_message(SimpleNamespace(content="oops")))
