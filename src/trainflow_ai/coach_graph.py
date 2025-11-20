"""LangGraph powered workflow for the AI endurance coach."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Protocol, TypedDict

from langgraph.graph import END, StateGraph

if TYPE_CHECKING:
    from langgraph.graph.graph import CompiledGraph

PROMPT_TEMPLATE = "You are an experienced endurance coach. Provide a short training plan in response to: {question}."


class LLMCallable(Protocol):
    """Protocol describing the callable contract expected from an LLM."""

    def __call__(self, prompt: str, /) -> str:  # pragma: no cover - typing helper
        """Return a model completion for the supplied prompt."""


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
            raise ValueError(msg)
        prompt = PROMPT_TEMPLATE.format(question=question)
        reply = llm(prompt)
        return {**state, "response": reply}

    return node


def build_coach_graph(llm: LLMCallable) -> CompiledGraph[CoachState]:
    """Return a compiled one-node LangGraph that delegates to the provided LLM."""

    graph = StateGraph(CoachState)
    graph.add_node("llm", _llm_node(llm))
    graph.set_entry_point("llm")
    graph.add_edge("llm", END)
    return graph.compile()
