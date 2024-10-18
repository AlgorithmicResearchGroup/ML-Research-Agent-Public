import os
from openai import OpenAI
from agent.utils import anthropic_to_openai


return_fn_tool_definitions = [
    {
        "name": "return_fn",
        "description": "Formats results of the subtask.",
        "input_schema": {
            "type": "object",
            "properties": {
                "submission": {
                    "type": "string",
                    "description": "The metrics of the subtask.",
                },
                "model_path": {
                    "type": "string",
                    "description": "Path to the trained model or artifact",
                },
            },
            "required": ["submission", "model_path"],
        },
    }
]


def return_fn(arguments):
    """
    This function is used to return the answer to the task.
    Use this function to run the code you need to complete the task.
    """
    submission = arguments["submission"]
    model_path = arguments["model_path"]

    try:
        return {
            "tool": "return_fn",
            "submission": submission,
            "model_path": model_path,
        }

    except Exception as e:
        return {
            "tool": "return_fn",
            "submission": submission,
            "model_path": model_path,
        }
