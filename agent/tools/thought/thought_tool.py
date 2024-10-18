import os

thought_tool_definitions = [
    {
        "name": "thought",
        "description": "Record your thoughts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "The thought that you just had.",
                },
            },
            "required": ["thought"],
        },
    },
]


class Thought:
    def return_thought(self, thought):
        try:
            return {
                "tool": "thought",
                "status": "success",
                "attempt": f"You had a thought",
                "stdout": f"{thought}",
                "stderr": "",
            }
        except Exception as e:
            return {
                "tool": "thought",
                "status": "failure",
                "attempt": "You failed to think",
                "stdout": "You failed to think",
                "stderr": str(e),
            }


def use_thought(arguments):  # write to the scratchpad file
    """
    This function is used to write to the scratchpad file.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        thought = arguments["thought"]
    else:
        thought = arguments

    thought_tool = Thought()
    result = thought_tool.return_thought(thought)
    return result
