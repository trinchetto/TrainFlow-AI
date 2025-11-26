"""LangGraph powered workflow for the AI endurance coach."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Protocol, TypedDict, cast

from langgraph.graph import END, StateGraph

from trainflow_ai.logging_utils import StructuredLogger

if TYPE_CHECKING:
    from langgraph.graph.graph import CompiledGraph

logger = StructuredLogger("trainflow_ai.coach_graph")

PROMPT_TEMPLATE = "You are an experienced endurance coach. Provide a short training plan in response to: {question}."


class LLMCallable(Protocol):
    """Protocol describing the callable contract expected from an LLM."""

    def __call__(self, prompt: str, /) -> str:  # pragma: no cover - typing helper
        """Return a model completion for the supplied prompt."""
        ...


class CoachState(TypedDict, total=False):
    """Mutable state that flows through the LangGraph."""

    question: str
    response: str


def _llm_node(llm: LLMCallable) -> Callable[[CoachState], CoachState]:
    """Wrap the LLM callable so it can be attached to the graph."""

    def node(state: CoachState) -> CoachState:
        question = state.get("question")
        if question is None:
            msg = "Coach graph requires a 'question' field in the state"
            logger.error("Missing question in coach graph state")
            raise ValueError(msg)

        logger.info("Processing coaching request", question_length=len(question))

        prompt = PROMPT_TEMPLATE.format(question=question)
        logger.debug("Formatted coaching prompt", prompt_length=len(prompt))

        try:
            reply = llm(prompt)
            logger.info("Generated coaching response", response_length=len(reply))
        except Exception as exc:
            logger.error(
                "LLM invocation failed",
                error_type=type(exc).__name__,
                error_message=str(exc),
                exc_info=exc,
            )
            return {
                **state,
                "response": (
                    "I apologize, but I'm having trouble generating a training plan right now. "
                    "Please try again."
                ),
            }

        return {**state, "response": reply}

    return node


@logger.with_error_handling(reraise=True)
def build_coach_graph(llm: LLMCallable) -> "CompiledGraph[CoachState]":
    """Return a compiled one-node LangGraph that delegates to the provided LLM."""

    logger.info("Building coach graph")

    graph = StateGraph(CoachState)
    graph.add_node("llm", cast(Any, _llm_node(llm)))
    graph.set_entry_point("llm")
    graph.add_edge("llm", END)

    compiled_graph = graph.compile()

    logger.info("Coach graph built successfully")

    return compiled_graph
