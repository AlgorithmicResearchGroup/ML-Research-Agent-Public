import logging
import shlex
import subprocess
from typing import Dict, Optional
from agent.utils import remove_ascii

bash_tool_definitions = [
    {
        "name": "run_bash",
        "description": "Run a bash script on the server. Doesn't support interactive commands",
        "input_schema": {
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "description": "The bash script to run.",
                },
            },
            "required": ["script"],
        },
    },
]


class BashRunnerActor:
    def __init__(self, timeout: int = 1000000):
        self.timeout = timeout

    def run(self, command: str) -> Dict[str, Optional[str]]:
        """Method to execute a bash command and return the results."""
        logging.info(f"Executing command: {command}")

        result = {
            "tool": "run_bash",
            "status": "failure",
            "returncode": None,
            "attempt": command,
            "stdout": "",
            "stderr": "",
        }

        try:
            # Start the subprocess with unbuffered output
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            stdout_lines = []
            stderr_lines = []

            import threading
            import sys

            def read_stdout():
                for line in iter(process.stdout.readline, ''):
                    print(line, end='')  # Print to console
                    stdout_lines.append(line)

            def read_stderr():
                for line in iter(process.stderr.readline, ''):
                    print(line, end='', file=sys.stderr)  # Print errors to stderr
                    stderr_lines.append(line)

            stdout_thread = threading.Thread(target=read_stdout)
            stderr_thread = threading.Thread(target=read_stderr)

            stdout_thread.start()
            stderr_thread.start()

            # Wait for the process to finish
            process.wait(timeout=self.timeout)

            # Wait for threads to finish reading
            stdout_thread.join()
            stderr_thread.join()

            returncode = process.returncode
            result['returncode'] = returncode

            result["stdout"] = ''.join(stdout_lines)
            result["stderr"] = ''.join(stderr_lines)

            if returncode == 0:
                result["status"] = "success"
            else:
                result["status"] = "failure"
                logging.error(f"Command failed with returncode: {returncode}")
                logging.error(f"Command stderr:\n{result['stderr']}")

            return result

        except subprocess.TimeoutExpired:
            process.kill()
            stdout_thread.join()
            stderr_thread.join()
            result["stderr"] = f"Command timed out after {self.timeout} seconds"
            logging.error(result["stderr"])
            return result

        except Exception as e:
            process.kill()
            stdout_thread.join()
            stderr_thread.join()
            result["stderr"] = f"Unexpected error: {str(e)}"
            logging.exception(result["stderr"])
            return result


def run_bash(arguments: dict) -> Dict[str, Optional[str]]:
    """
    This function is used to run a bash script on the server.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        command = arguments["script"]
    else:
        command = arguments

    runner_actor = BashRunnerActor()
    result = runner_actor.run(command)
    result["stdout"] = remove_ascii(result["stdout"])
    return result
