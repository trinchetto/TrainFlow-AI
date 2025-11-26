"""Chainlit entrypoint wiring the UI to the LangGraph powered coach."""

from __future__ import annotations

import os
import uuid
from typing import Any, Awaitable, Callable, Optional, cast

import chainlit as cl
from langchain_openai import ChatOpenAI

from trainflow_ai.coach_graph import CoachState, LLMCallable, build_coach_graph
from trainflow_ai.logging_utils import StructuredLogger, set_correlation_id, set_user_session_id

logger = StructuredLogger("trainflow_ai.chainlit_app", os.getenv("LOG_LEVEL", "INFO"))

DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
GraphRunner = Callable[[CoachState], Awaitable[CoachState]]


@logger.with_error_handling(fallback_response="Error: Could not serialize response")
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


@logger.with_error_handling()
def _openai_llm() -> LLMCallable:
    model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
    chat = ChatOpenAI(model=model, temperature=temperature)
    logger.info("Initializing OpenAI LLM", model=model, temperature=temperature)

    @logger.with_error_handling(
        fallback_response="I apologize, but I'm having trouble generating a response right now. Please try again."
    )
    def invoke(prompt: str) -> str:
        logger.debug("Invoking OpenAI LLM", prompt_length=len(prompt))
        message = chat.invoke(prompt)
        response = _serialize_response(message)
        logger.info("OpenAI LLM response generated", response_length=len(response))
        return response

    return invoke


@logger.with_error_handling()
def _fallback_llm() -> LLMCallable:
    def invoke(prompt: str) -> str:
        logger.info("Using fallback LLM", prompt_length=len(prompt))
        response = (
            "(Fallback response) Here is a simple training plan based on your request: " f"{prompt}"
        )
        logger.debug("Fallback LLM response generated", response_length=len(response))
        return response

    return invoke


@logger.with_error_handling()
def _build_llm_callable() -> LLMCallable:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        logger.info("Using OpenAI LLM with API key")
        return _openai_llm()
    logger.warning(
        "OPENAI_API_KEY not set. Falling back to deterministic responses for Chainlit UI."
    )
    return _fallback_llm()


@logger.with_error_handling()
def _build_runner() -> GraphRunner:
    logger.info("Building LangGraph runner")
    graph = build_coach_graph(_build_llm_callable())
    runner = cast(GraphRunner, cl.make_async(graph.invoke))
    logger.info("LangGraph runner built successfully")
    return runner


def _get_runner() -> GraphRunner:
    session_store = cast(Any, cl.user_session)
    runner: Optional[GraphRunner] = session_store.get("graph_runner")
    if runner is None:
        runner = _build_runner()
        session_store.set("graph_runner", runner)
    return runner


@cl.on_chat_start  # type: ignore[misc]
@logger.with_error_handling(reraise=True)
async def on_chat_start() -> None:
    """Initialize the LangGraph runner when the user session begins."""

    # Generate session ID for tracking
    session_id = str(uuid.uuid4())
    set_user_session_id(session_id)

    logger.info("Starting new chat session", session_id=session_id)

    session_store = cast(Any, cl.user_session)
    runner = _build_runner()
    session_store.set("graph_runner", runner)
    session_store.set("session_id", session_id)

    welcome_message = (
        "Hi! Tell me how much time you have and how you're feeling, "
        "and I'll craft a training plan."
    )

    await cast(Any, cl.Message(welcome_message)).send()

    logger.info("Chat session initialized successfully", session_id=session_id)


@cl.on_message  # type: ignore[misc]
@logger.with_error_handling(reraise=True)
async def on_message(message: cl.Message) -> None:
    """Forward the user prompt to the LangGraph pipeline and surface the result."""

    # Get or create correlation ID for this request
    request_id = str(uuid.uuid4())
    set_correlation_id(request_id)

    session_store = cast(Any, cl.user_session)
    session_id = session_store.get("session_id")
    if session_id:
        set_user_session_id(session_id)

    logger.info(
        "Processing user message",
        request_id=request_id,
        session_id=session_id,
        message_length=len(message.content) if message.content else 0,
    )

    runner = _get_runner()
    state: CoachState = {"question": message.content}

    logger.debug("Invoking LangGraph", request_id=request_id)
    result = await runner(state)

    reply = result.get("response") or "I could not generate a response, please try again."

    logger.info(
        "Response generated successfully",
        request_id=request_id,
        response_length=len(reply),
    )

    await cast(Any, cl.Message(content=reply)).send()
