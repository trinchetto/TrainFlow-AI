"""Example test module.

This demonstrates the test structure for the project.
Replace with your actual tests.
"""

import pytest


def test_example() -> None:
    """Example test case."""
    assert True


def test_example_with_fixture(sample_data: str) -> None:
    """Example test using a fixture."""
    assert sample_data == "test data"


@pytest.fixture
def sample_data() -> str:
    """Example fixture."""
    return "test data"


class TestExampleClass:
    """Example test class grouping related tests."""

    def test_method_one(self) -> None:
        """Test method one."""
        assert 1 + 1 == 2

    def test_method_two(self) -> None:
        """Test method two."""
        assert "hello" in "hello world"
