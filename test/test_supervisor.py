import os
import pytest
import json
from unittest.mock import patch, MagicMock
from agent.supervisor import Supervisor


@pytest.fixture
def mock_environment(monkeypatch):
    monkeypatch.setenv("OPENAI", "test_openai_key")
    monkeypatch.setenv("ANTHROPIC", "test_anthropic_key")


@pytest.fixture
def supervisor(mock_environment):
    return Supervisor()


def test_supervisor_initialization(supervisor):
    assert supervisor.agent_model == "openai"
    assert supervisor.oai_client is not None
    assert supervisor.client is not None
    assert supervisor.system_prompt is not None


@patch("openai.OpenAI.ChatCompletion.create")
def test_generate_plan_openai(mock_openai_create, supervisor):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.tool_calls = [MagicMock()]
    mock_response.choices[0].message.tool_calls[0].function.arguments = json.dumps(
        {"plan": ["Step 1", "Step 2"]}
    )
    mock_openai_create.return_value = mock_response

    task = "Test task"
    response = supervisor.generate_plan(task)
    assert response is not None
    mock_openai_create.assert_called_once()


@patch("anthropic.Anthropic.ChatCompletion.create")
def test_generate_plan_anthropic(mock_anthropic_create, supervisor):
    supervisor.agent_model = "anthropic"
    mock_response = MagicMock()
    mock_response.content = [{"input": {"plans": [{"plan": ["Step 1", "Step 2"]}]}}]
    mock_anthropic_create.return_value = mock_response

    task = "Test task"
    response = supervisor.generate_plan(task)
    assert response is not None
    mock_anthropic_create.assert_called_once()


def test_parse_chat_response_to_subtasks_openai(supervisor):
    mock_chat_response = MagicMock()
    mock_chat_response.choices = [MagicMock()]
    mock_chat_response.choices[0].message.tool_calls = [MagicMock()]
    mock_chat_response.choices[0].message.tool_calls[0].function.arguments = json.dumps(
        {"plan": ["Step 1", "Step 2"]}
    )

    parsed_subtasks = supervisor.parse_chat_response_to_subtasks(mock_chat_response)
    assert parsed_subtasks == [[{"Subtask": "Step 1"}, {"Subtask": "Step 2"}]]


def test_parse_chat_response_to_subtasks_anthropic(supervisor):
    supervisor.agent_model = "anthropic"
    mock_chat_response = MagicMock()
    mock_chat_response.content = [
        {"input": {"plans": [{"plan": ["Step 1", "Step 2"]}]}}
    ]

    parsed_subtasks = supervisor.parse_chat_response_to_subtasks(mock_chat_response)
    assert parsed_subtasks == [[{"Subtask": "Step 1"}, {"Subtask": "Step 2"}]]


@patch("agent.supervisor.Worker")
@patch.object(Supervisor, "generate_plan", return_value=MagicMock())
@patch.object(
    Supervisor,
    "parse_chat_response_to_subtasks",
    return_value=[[{"Subtask": "Step 1"}, {"Subtask": "Step 2"}]],
)
def test_run(
    mock_parse_chat_response_to_subtasks, mock_generate_plan, mock_worker, supervisor
):
    mock_worker_instance = mock_worker.return_value
    mock_worker_instance.run.return_value = {"result": "success"}

    user_id = 1
    run_id = 1
    task = "Test task"
    task_number = 1

    result = supervisor.run(user_id, run_id, task, task_number)
    assert result == {"result": "success"}
    mock_generate_plan.assert_called_once_with(task)
    mock_parse_chat_response_to_subtasks.assert_called_once()
    mock_worker.assert_called_once_with(
        user_id,
        run_id,
        user_query=task,
        plan="Plan 0 --->\nStep 1\nStep 2\n\n",
        worker_number=1,
    )
    mock_worker_instance.run.assert_called_once()


if __name__ == "__main__":
    pytest.main()
