import os

code_tool_definitions = [
    {
        "name": "write_code",
        "description": "Write code to a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to write",
                },
                "code": {
                    "type": "string",
                    "description": "The code to write to the file.",
                },
            },
            "required": ["path", "code"],
        },
    },
    # {
    #     "name": "read_code",
    #     "description": "Read code from a file.",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "path": {
    #                 "type": "string",
    #                 "description": "The path to the file to read.",
    #             },
    #         },
    #         "required": ["path"],
    #     },
    # },
    {
        "name": "insert_code",
        "description": "Insert code into a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to insert code into.",
                },
                "target": {
                    "type": "string",
                    "description": "The existing code snippet after which you want to insert the new code.",
                },
                "new_code": {
                    "type": "string",
                    "description": "The new code snippet you want to insert.",
                },
            },
            "required": ["target", "new_code"],
        },
    },
    {
        "name": "replace_code",
        "description": "Replace code in a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to insert code into.",
                },
                "old_code": {
                    "type": "string",
                    "description": "The existing code snippet you want to replace.",
                },
                "new_code": {
                    "type": "string",
                    "description": "The new code snippet you want to replace the old code with.",
                },
            },
            "required": ["old_code", "new_code"],
        },
    },
    {
        "name": "delete_code",
        "description": "Delete code from a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to insert code into.",
                },
                "target": {
                    "type": "string",
                    "description": "The code snippet you want to delete.",
                },
            },
            "required": ["target"],
        },
    },
]


class PythonEditorActor:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_code(self):
        try:
            with open(self.file_path, "r") as file:
                code = file.read()
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
            print(f"Creating file: {self.file_path}")
            with open(self.file_path, "w") as file:
                code = ""
        return code

    # def read_code_tool(self):
    #     try:
    #         with open(self.file_path, "r") as file:
    #             code = file.read()
    #         return {
    #                 "tool": "read_code",
    #                 "status": "success",
    #                 "attempt": f"You read the code in {self.file_path}",
    #                 "stdout": f"The code in the file is: \n {code}",
    #                 "stderr": "",
    #             }

    #     except Exception as e:
    #         return {
    #             "tool": "read_code",
    #             "status": "failure",
    #             "attempt": f"You tried to read the code in {self.file_path} but it failed",
    #             "stdout": str(e),
    #             "stderr": "Failed to read the code in the file",
    #         }

    def write_code(self, code):
        try:
            if not os.path.exists(self.file_path):  # Check if the file exists
                with open(self.file_path, "w") as file:  # Write the code to the file
                    file.write(code)
            else:
                with open(self.file_path, "w") as file:  # Write the code to the file
                    file.write(code)
            print(f"File saved: {self.file_path}")
            return {
                "tool": "write_code",
                "status": "success",
                "attempt": f"You wrote code to {self.file_path}",
                "stdout": f"You wrote this code: \n {code}",
                "stderr": "",
            }

        except IOError as e:
            print(f"Error saving file: {self.file_path}")
            print(f"Error details: {str(e)}")
            return {
                "tool": "write_code",
                "status": "failure",
                "attempt": f"You tried to write code to {self.file_path} but it failed",
                "stdout": "",
                "stderr": str(e),
            }

    def insert_code(self, target, new_code):
        code = self.read_code()
        if code is None:
            return {
                "tool": "insert_code",
                "status": "failure",
                "attempt": "insert_code",
                "stdout": "",
                "stderr": "No code found in the file",
            }

        target_index = code.find(target)
        if target_index != -1:
            modified_code = code[:target_index] + new_code + code[target_index:]
            self.write_code(modified_code)
            return {
                "tool": "insert_code",
                "status": "success",
                "attempt": f"You inserted code in {self.file_path}",
                "stdout": f"Inserted code after {target}",
                "stderr": "",
            }
        else:
            print(f"Target code not found: {target}")
            return {
                "tool": "insert_code",
                "status": "failure",
                "attempt": f"You tried to insert code after {target} but it failed",
                "stdout": "",
                "stderr": "Target code not found",
            }

    def replace_code(self, old_code, new_code):
        code = self.read_code()
        if code is None:
            return {
                "tool": "replace_code",
                "status": "failure",
                "attempt": "replace_code",
                "stdout": "",
                "stderr": "No code found in the file",
            }

        modified_code = code.replace(old_code, new_code)
        self.write_code(modified_code)
        return {
            "tool": "replace_code",
            "status": "success",
            "attempt": f"You replaced code in {self.file_path}",
            "stdout": f"This code {old_code} was replaced with {new_code}",
            "stderr": "",
        }

    def delete_code(self, target):
        code = self.read_code()
        if code is None:
            return {
                "tool": "delete_code",
                "status": "failure",
                "attempt": f"You tried to delet {target} but it failed",
                "stdout": "",
                "stderr": "No code found in the file",
            }

        modified_code = code.replace(target, "")
        self.write_code(modified_code)
        return {
            "tool": "delete_code",
            "status": "success",
            "attempt": f"You deleted code in {self.file_path}",
            "stdout": f"This code {target} was deleted",
            "stderr": "",
        }


# def read_code_tool(arguments):  # read code from a file
#     """
#     This function is used to read code from a file.
#     Use this function to run the code you need to complete the task.
#     """
#     if isinstance(arguments, dict):
#         path = arguments["path"]
#     else:
#         path = arguments

#     editor_actor = PythonEditorActor(path)
#     result = editor_actor.read_code_tool()
#     return result


def write_code(arguments):  # write code to a file
    """
    This function is used to write code to a file.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        path = arguments["path"]
        code = arguments["code"]
    else:
        path = arguments[0]
        code = arguments[1]

    editor_actor = PythonEditorActor(path)
    result = editor_actor.write_code(code)
    return result


def insert_code(arguments):  # insert code into a file
    """
    This function is used to insert code into a file.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        path = arguments["path"]
        target = arguments["target"]
        new_code = arguments["new_code"]
    else:
        path = arguments[0]
        target = arguments[1]
        new_code = arguments[2]

    editor_actor = PythonEditorActor(path)
    result = editor_actor.insert_code(target, new_code)
    return result


def replace_code(arguments):  # replace code in a file
    """
    This function is used to replace code in a file.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        path = arguments["path"]
        old_code = arguments["old_code"]
        new_code = arguments["new_code"]
    else:
        path = arguments[0]
        old_code = arguments[1]
        new_code = arguments[2]

    editor_actor = PythonEditorActor(path)
    result = editor_actor.replace_code(old_code, new_code)
    return result


def delete_code(arguments):  # delete code from a file
    """
    This function is used to delete code from a file.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        path = arguments["path"]
        target = arguments["target"]
    else:
        path = arguments[0]
        target = arguments[1]

    editor_actor = PythonEditorActor(path)
    result = editor_actor.delete_code(target)
    return result
