"""Chainlit entrypoint wiring the UI to the LangGraph powered coach."""

from __future__ import annotations

import logging
import os
from typing import Any, Awaitable, Callable, Optional, cast

import chainlit as cl

from trainflow_ai.coach_graph import CoachState, LLMCallable, build_coach_graph

logger = logging.getLogger(__name__)
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
GraphRunner = Callable[[CoachState], Awaitable[CoachState]]


def _serialize_response(message: Any) -> str:
    """Best-effort conversion from LangChain messages/objects to plain text."""

    if isinstance(message, str):
        return message
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for chunk in content:
            text = None
            if isinstance(chunk, dict):
                if chunk.get("type") == "text":
                    text = chunk.get("text")
            else:
                text = getattr(chunk, "text", None)
            if text:
                parts.append(text)
        if parts:
            return "".join(parts)
    return str(message)


def _openai_llm() -> LLMCallable:
    from langchain_openai import ChatOpenAI

    model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
    chat = ChatOpenAI(model=model, temperature=temperature)

    def invoke(prompt: str) -> str:
        message = chat.invoke(prompt)
        return _serialize_response(message)

    return invoke


def _fallback_llm() -> LLMCallable:
    def invoke(prompt: str) -> str:
        return (
            "(Fallback response) Here is a simple training plan based on your request: " f"{prompt}"
        )

    return invoke


def _build_llm_callable() -> LLMCallable:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return _openai_llm()
    logger.warning(
        "OPENAI_API_KEY not set. Falling back to deterministic responses for Chainlit UI."
    )
    return _fallback_llm()


def _build_runner() -> GraphRunner:
    graph = build_coach_graph(_build_llm_callable())
    return cast(GraphRunner, cl.make_async(graph.invoke))


def _get_runner() -> GraphRunner:
    runner: Optional[GraphRunner] = cl.user_session.get("graph_runner")
    if runner is None:
        runner = _build_runner()
        cl.user_session.set("graph_runner", runner)
    return runner


@cl.on_chat_start  # type: ignore[misc]
async def on_chat_start() -> None:
    """Initialize the LangGraph runner when the user session begins."""

    runner = _build_runner()
    cl.user_session.set("graph_runner", runner)
    await cl.Message(
        "Hi! Tell me how much time you have and how you're feeling, and I'll craft a training plan."
    ).send()


@cl.on_message  # type: ignore[misc]
async def on_message(message: cl.Message) -> None:
    """Forward the user prompt to the LangGraph pipeline and surface the result."""

    runner = _get_runner()
    state: CoachState = {"question": message.content}
    result = await runner(state)
    reply = result.get("response") or "I could not generate a response, please try again."
    await cl.Message(content=reply).send()
