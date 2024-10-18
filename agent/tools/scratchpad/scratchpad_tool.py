import os

scratchpad_tool_definitions = [
    {
        "name": "scratchpad",
        "description": "Write and read important findings to and from a scratchpad file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the scratchpad file.",
                },
                "note": {
                    "type": "string",
                    "description": "The note to write to the scratchpad file. If action is 'read', pass an empty string.",
                },
                "action": {
                    "type": "string",
                    "description": "The action to perform. Either 'write' or 'read'.",
                },
            },
            "required": ["path", "note", "action"],
        },
    },
]


class ScratchPad:
    def write_note(self, path: str, note: str) -> dict:
        try:
            if not os.path.exists(path):
                with open(path, "w") as file:
                    text = "start of notes file"
                    file.write(text)
            with open(path, "a") as file:
                file.write(note + "\n \n")
            return {
                "tool": "write_note",
                "status": "success",
                "attempt": f"You wrote a note in {path}",
                "stdout": note,
                "stderr": "",
            }
        except Exception as e:
            return {
                "tool": "write_note",
                "status": "failure",
                "attempt": "You failed to write a note",
                "stdout": "You failed to write a note",
                "stderr": str(e),
            }

    def read_notes(self, path: str) -> dict:
        try:
            if not os.path.exists(path):
                with open(path, "w") as file:
                    text = "start of notes file"
                    file.write(text)
            with open(path, "r") as file:
                notes = file.read()
            return {
                "tool": "read_notes",
                "status": "success",
                "attempt": f"You read the notes in {path}",
                "stdout": notes,
                "stderr": "",
            }
        except Exception as e:
            return {
                "tool": "read_notes",
                "status": "failure",
                "attempt": f"You failed to read the notes in {path}",
                "stdout": "",
                "stderr": str(e),
            }


def use_scratchpad(arguments: dict) -> dict:  # write to the scratchpad file
    """
    This function is used to write to the scratchpad file.
    Use this function to run the code you need to complete the task.
    """
    path = arguments["path"]
    note = arguments["note"]
    action = arguments["action"]

    scratchpad = ScratchPad()
    if action == "write":
        result = scratchpad.write_note(path, note)
    elif action == "read":
        result = scratchpad.read_notes(path)
    else:
        result = {
            "tool": "scratchpad",
            "status": "failure",
            "attempt": "scratchpad",
            "stdout": "",
            "stderr": "Invalid action. Please specify 'write' or 'read'.",
        }
    return result
