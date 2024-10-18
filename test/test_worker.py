import pytest
import os
import random
import json
from unittest.mock import patch, MagicMock
from worker import Worker


@pytest.fixture
def mock_environment(monkeypatch):
    monkeypatch.setenv("OPENAI", "test_openai_key")
    monkeypatch.setenv("ANTHROPIC", "test_anthropic_key")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")
    monkeypatch.setenv("DB_HOST", "test_host")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test_db")


@pytest.fixture
def worker(mock_environment):
    return Worker(
        user_id=1, run_id=1, user_query="Test Query", plan="Test Plan", worker_number=1
    )


def test_worker_initialization(worker):
    assert worker.user_id == 1
    assert worker.run_id == 1
    assert worker.user_query == "Test Query"
    assert worker.plan == "Test Plan"
    assert worker.worker_number == 1
    assert worker.task_number == 0


@patch("os.makedirs")
def test_make_directory(mock_makedirs, worker):
    random_number = random.getrandbits(32)
    worker.make_directory(random_number)
    mock_makedirs.assert_called_once_with(f"{os.getcwd()}/{worker.run_number}")


@patch("os.system")
def test_git_clone(mock_system, worker):
    worker.make_directory(worker.run_number)
    git_clone_command = f"git clone git@github.com:Artifact-AI/ai_research_bench.git {os.getcwd()}/{worker.run_number}/ai_research_bench"
    assert mock_system.call_count == 5
    mock_system.assert_any_call(git_clone_command)


@patch(
    "worker.Worker.run_subtask",
    return_value={
        "subtask_result": {
            "tool": "test_tool",
            "status": "success",
            "attempt": "test_attempt",
            "stdout": "test_output",
            "stderr": "test_errors",
        },
        "attempted": "yes",
    },
)
def test_process_subtasks(mock_run_subtask, worker):
    result = worker.process_subtasks()
    assert result["plan"] == "Test Plan"
    assert result["result"] == "test_attempt"
    assert result["total_tokens"] == 0
    assert result["total_turns"] == "1"
    assert result["run_number"] == str(worker.run_number)


def test_run(worker):
    with patch.object(
        worker, "process_subtasks", return_value={"result": "success"}
    ) as mock_process_subtasks:
        result = worker.run()
        assert result["result"] == "success"
        mock_process_subtasks.assert_called_once()


if __name__ == "__main__":
    pytest.main()
