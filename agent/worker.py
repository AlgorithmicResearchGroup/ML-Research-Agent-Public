import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import traceback

from rich import print
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from rich.columns import Columns

from agent.memory import AgentMemory
from agent.tool_registry import Tool, worker_action_map
from agent.memory import Base
from agent.tool_registry import all_tools
from agent.prompts import get_worker_system_prompt, get_worker_prompt
from agent.models.anthropic import AnthropicModel
from agent.models.openai import OpenAIModel

load_dotenv()
console = Console()


class Worker:
    def __init__(
        self,
        user_id=int,
        run_id=int,
        user_query=str,
        plan=str,
        worker_number=int,
        provider=str,
    ) -> None:
        self.user_id = user_id
        self.run_id = run_id
        self.agent_model = provider
        self.user_query = user_query
        self.plan = plan
        self.worker_number = worker_number
        self.task_number = 0
        self.num_tokens = []
        self.run_number = run_id
        self.start_time = datetime.now()

        self.plan_structure = {"subtasks": [], "completed": [], "in_progress": None}
        self.system_prompt = get_worker_system_prompt(self.run_number)
        self.make_directory(self.run_id)

        self.memory = AgentMemory()
        
        
    def make_directory(self, work_dir):
        work_dir = f"./{work_dir}"
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
        os.system(
            f"touch {work_dir}/scratchpad.txt"
        )
        with open(f"{work_dir}/scratchpad.txt", "w") as scratchpad:
            scratchpad.write("This is a scratchpad file for you to write notes on your task.")

    def pretty_attempt(self, content):
        return f"[yellow] Total Tokens: {sum(self.num_tokens)} --> Previous Attempt: {content}"

    def pretty_output(self, content):
        return f"[blue] Total Tokens: {sum(self.num_tokens)} --> Previous Output: {content}"

    def run_subtask(
        self,
        previous_subtask_attempt,
        previous_subtask_output,
        previous_subtask_errors,
        elapsed_time,
    ) -> dict:
        memories = self.memory.get_conversation_memory(self.run_id)

        self.prompt = get_worker_prompt(
            self.user_query,
            self.plan,
            self.run_number,
            memories,
            elapsed_time,
            previous_subtask_attempt,
            previous_subtask_output,
            previous_subtask_errors,
        )

        try:
            if self.task_number > 0:  # Only print if it's not the first iteration
                if isinstance(previous_subtask_attempt, str):
                    user_renderables = [
                        Panel(
                            self.pretty_attempt(previous_subtask_attempt), expand=True
                        ),
                        Panel(self.pretty_output(previous_subtask_output), expand=True),
                    ]
                    console.print(Panel(Columns(user_renderables)))
                else:
                    print(
                        f"""
                            Previous Attempt: {previous_subtask_attempt}
                            Previous Output: {previous_subtask_output}
                        """
                    )

            if self.agent_model == "openai":
                (
                    response_data,
                    total_tokens,
                    prompt_tokens,
                    response_tokens,
                ) = OpenAIModel(self.system_prompt, all_tools).generate_response(
                    self.prompt
                )
            else:
                (
                    response_data,
                    total_tokens,
                    prompt_tokens,
                    response_tokens,
                ) = AnthropicModel(self.system_prompt, all_tools).generate_response(
                    self.prompt
                )

            self.num_tokens.append(total_tokens)
            print(f"Number of tokens: {total_tokens}")

            if not response_data:
                print("No response data found.")
                return {
                    "subtask_result": "Invalid response",
                    "subtask_status": "failure",
                }

            if isinstance(response_data, dict):
                # Iterate through the action_map
                for key, val in worker_action_map.items():
                    # Check if val is a string and directly check for existence
                    if isinstance(val, str):
                        if val in response_data:
                            # print(f"Action {key} is applicable with {val}")
                            tool_output = Tool(
                                {
                                    "type": "function",
                                    "function": {
                                        "name": key,
                                        "parameters": response_data[val],
                                    },
                                }
                            )
                            tool_output = tool_output.run()
                            return {
                                "subtask_result": tool_output,
                                "attempted": "yes",
                                "total_tokens": total_tokens,
                                "prompt_tokens": prompt_tokens,
                                "response_tokens": response_tokens,
                            }
                    # If val is a list, iterate through the list and check each item
                    elif isinstance(val, list):
                        if all(
                            k in response_data for k in val
                        ):  # All keys in the list must be in response_data
                            # print(f"Action {key} is applicable with {val}")
                            tool_output = Tool(
                                {
                                    "type": "function",
                                    "function": {
                                        "name": key,
                                        "parameters": response_data,
                                    },
                                }
                            )
                            tool_output = tool_output.run()
                            return {
                                "subtask_result": tool_output,
                                "attempted": "yes",
                                "total_tokens": total_tokens,
                                "prompt_tokens": prompt_tokens,
                                "response_tokens": response_tokens,
                            }
            else:
                return {
                    "subtask_result": response_data,
                    "attempted": "yes",
                    "total_tokens": total_tokens,
                    "prompt_tokens": prompt_tokens,
                    "response_tokens": response_tokens,
                }

        except Exception as e:
            print(
                f"An error occurred in the Worker: {str(e)} on line {e.__traceback__.tb_lineno}"
            )
            traceback.print_exc()
            return {
                "subtask_result": {
                    "tool": "None",
                    "status": "failure",
                    "attempt": f"An error occurred: {str(e)}",
                    "stdout": "None",
                    "stderr": "None",
                },
                "attempted": "no",
                "total_tokens": 0,
                "prompt_tokens": 0,
                "response_tokens": 0,
            }

    def process_subtasks(self):
        results = []

        previous_subtask_tool = "You are starting the task"
        previous_subtask_attempt = "You are starting the task"
        previous_subtask_result = "This is your first attempt"
        previous_subtask_output = "You are starting the task"
        previous_subtask_errors = "You are starting the task"
        self.task_number = 0
        total_tokens = 0
        prompt_tokens = 0
        response_tokens = 0

        self.memory.save_conversation_memory(
            self.user_id,
            self.run_id,
            previous_subtask_tool,
            previous_subtask_result,
            previous_subtask_attempt,
            previous_subtask_output,
            previous_subtask_errors,
            total_tokens,
            prompt_tokens,
            response_tokens,
        )

        while True:
            current_time = datetime.now()

            elapsed_time = current_time - self.start_time
            subtask_response = self.run_subtask(
                previous_subtask_attempt,
                previous_subtask_output,
                previous_subtask_errors,
                elapsed_time,
            )
            if self.task_number > 0:
                try:
                    previous_subtask_tool = subtask_response["subtask_result"]["tool"]
                    previous_subtask_result = subtask_response["subtask_result"][
                        "status"
                    ]
                    previous_subtask_attempt = subtask_response["subtask_result"][
                        "attempt"
                    ]
                    previous_subtask_output = subtask_response["subtask_result"][
                        "stdout"
                    ]
                    previous_subtask_errors = subtask_response["subtask_result"][
                        "stderr"
                    ]
                    total_tokens = subtask_response["total_tokens"]
                    prompt_tokens = subtask_response["prompt_tokens"]
                    response_tokens = subtask_response["response_tokens"]

                    self.memory.save_conversation_memory(
                        self.user_id,
                        self.run_id,
                        previous_subtask_tool,
                        previous_subtask_result,
                        previous_subtask_attempt,
                        previous_subtask_output,
                        previous_subtask_errors,
                        total_tokens,
                        prompt_tokens,
                        response_tokens,
                    )
                except Exception as e:
                    print(f"An error occurred: {e}")
                    traceback.print_exc()  # This will print the full stack trace
                    if isinstance(subtask_response, str):
                        panel = Panel(
                            Text(f"Thought: {str(subtask_response)}"), style="on green"
                        )
                        print(panel)
                    else:
                        print(subtask_response)

                    previous_subtask_tool = "thought"
                    previous_subtask_attempt = (
                        f"You had the thought: {subtask_response}"
                    )
                    previous_subtask_result = "You had a thought"
                    previous_subtask_output = (
                        "you must now use a tool to complete the task"
                    )
                    previous_subtask_errors = "None"
                    total_tokens = 0
                    prompt_tokens = 0
                    response_tokens = 0

                    self.memory.save_conversation_memory(
                        self.user_id,
                        self.run_id,
                        previous_subtask_tool,
                        previous_subtask_result,
                        previous_subtask_attempt,
                        previous_subtask_output,
                        previous_subtask_errors,
                        total_tokens,
                        prompt_tokens,
                        response_tokens,
                    )

            results.append(subtask_response)
            self.task_number += 1
            if "return_fn" in previous_subtask_attempt:
                print(
                    f"Plan execution complete. Worker number {self.worker_number} completed the task"
                )
                return {
                    "plan": self.plan,
                    "result": previous_subtask_attempt,
                    "total_tokens": sum(self.num_tokens),
                    "total_turns": str(self.task_number),
                    "run_number": str(self.run_number),
                }

    def run(self):
        worker_result = self.process_subtasks()
        return worker_result
