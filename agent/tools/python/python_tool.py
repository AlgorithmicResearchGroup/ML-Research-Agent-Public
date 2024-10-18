import sys
import os
import io
import subprocess
from agent.utils import remove_ascii

python_tool_definitions = [
    {
        "name": "run_python",
        "description": "Run python code on the server. You must print the output",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "The path to a python file.",
                },
            },
            "required": ["filepath"],
        },
    },
]


class PythonRunnerActor:
    def __init__(self):
        pass  # No longer need the IPython shell instance

    def execute_python_code(self, filepath, timeout=None):
        result = {
            "tool": "run_python",
            "status": "failure",
            "attempt": filepath,
            "stdout": "",
            "stderr": "",
        }
        try:
            if os.path.isfile(filepath):
                # Use subprocess to run the script with unbuffered output
                process = subprocess.Popen(
                    [sys.executable, '-u', filepath],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1,
                )

                stdout_lines = []
                stderr_lines = []

                # Import threading to read stdout and stderr concurrently
                import threading

                def read_stdout():
                    for line in process.stdout:
                        print(line, end='')  # Print to console
                        stdout_lines.append(line)

                def read_stderr():
                    for line in process.stderr:
                        print(line, end='', file=sys.stderr)  # Print errors to stderr
                        stderr_lines.append(line)

                # Start threads to read stdout and stderr
                stdout_thread = threading.Thread(target=read_stdout)
                stderr_thread = threading.Thread(target=read_stderr)

                stdout_thread.start()
                stderr_thread.start()

                # Wait for the process to finish and threads to complete
                process.wait()
                stdout_thread.join()
                stderr_thread.join()

                # Get the return code
                return_code = process.returncode

                result["stdout"] = ''.join(stdout_lines)
                result["stderr"] = ''.join(stderr_lines)

                if return_code == 0:
                    result["status"] = "success"
                else:
                    result["status"] = "failure"

            else:
                raise FileNotFoundError(f"File not found: {filepath}")

        except Exception as e:
            # Handling unexpected errors
            result["stderr"] = str(e)

        return result

    def run_code(self, filepath, timeout=None):
        """Wrapper method to execute Python code using the actor's execution method with an optional timeout."""
        return self.execute_python_code(filepath)


def run_python(arguments):  # run python code on the server
    """
    This function is used to run python code.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        script = arguments["filepath"]
    else:
        script = arguments

    python_runner_actor = PythonRunnerActor()
    result = python_runner_actor.run_code(script)
    result["stdout"] = remove_ascii(result["stdout"])
    return result
