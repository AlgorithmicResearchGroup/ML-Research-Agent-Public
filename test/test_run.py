import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from run import run_task, parse_json


@pytest.fixture
def mock_supervisor():
    with patch("run.Supervisor") as mock:
        mock.return_value.run.return_value = {
            "result": '{"subtask_result": {"submission": "test", "model_path": "test_path"}}',
            "run_number": 123,
            "total_tokens": 100,
            "total_turns": 5,
            "plan": "Test plan",
        }
        yield mock


@pytest.fixture
def mock_task_family():
    with patch("run.TaskFamily") as mock:
        mock.return_value.install.return_value = "Test prompt"
        yield mock


def test_run_task(mock_supervisor, mock_task_family, capsys):
    result = run_task("mini_baby_lm", "mini_benchmark", "openai")

    captured = capsys.readouterr()

    assert result is not None
    assert "result" in result
    assert "run_number" in result
    assert "total_tokens" in result
    assert "total_turns" in result
    assert "plan" in result

    assert "Test prompt" in captured.out


def test_parse_json():
    test_string = "Some text {'key': 'value'} more text"
    result = parse_json(test_string)
    assert result == {"key": "value"}


@pytest.mark.parametrize(
    "task_name,benchmark,provider",
    [
        ("mini_baby_lm", "mini_benchmark", "openai"),
        ("llm_efficiency", "full_benchmark", "anthropic"),
    ],
)
def test_run_task_with_different_params(
    task_name, benchmark, provider, mock_supervisor, mock_task_family
):
    result = run_task(task_name, benchmark, provider)
    assert result is not None
    mock_task_family.return_value.install.assert_called_once_with(
        pytest.approx(result["run_number"]), benchmark, task_name
    )
    mock_supervisor.return_value.run.assert_called_once_with(
        1, pytest.approx(result["run_number"]), "Test prompt", task_name, provider
    )


def test_print_markdown_table(capsys):
    results = [
        ("Task Number", "mini_baby_lm"),
        ("Run ID", 123),
        ("Submission", "test"),
    ]
    from run import print_markdown_table

    print_markdown_table(results)
    captured = capsys.readouterr()
    assert "| Task Number                | mini_baby_lm |" in captured.out
    assert "| Run ID                     | 123         |" in captured.out
    assert "| Submission                 | test        |" in captured.out
