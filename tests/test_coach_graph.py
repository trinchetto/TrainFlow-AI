from unittest.mock import Mock

import pytest

from trainflow_ai.coach_graph import PROMPT_TEMPLATE, build_coach_graph


def test_coach_graph_invokes_llm_with_question() -> None:
    llm = Mock(return_value="Run 5km easy")
    graph = build_coach_graph(llm)

    result = graph.invoke({"question": "How should I train today?"})

    assert result["response"] == "Run 5km easy"
    llm.assert_called_once()
    prompt_arg = llm.call_args.args[0]
    assert "How should I train today?" in prompt_arg
    assert PROMPT_TEMPLATE.split("{")[0].strip() in prompt_arg


def test_coach_graph_requires_question() -> None:
    llm = Mock(return_value="anything")
    graph = build_coach_graph(llm)

    with pytest.raises(ValueError):
        graph.invoke({"question": None})
