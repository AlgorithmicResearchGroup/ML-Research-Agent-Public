import json
import anthropic
from openai import OpenAI
from argparse import ArgumentParser
from typing import TypedDict
from dotenv import load_dotenv
import os
import tiktoken
import traceback
from agent.worker import Worker
from agent.prompts import get_supervisor_system_prompt

# load environment variables
load_dotenv()

class Supervisor:
    def __init__(self):
        """Initialize the agent.
        input: task, instructions
        output: final_command
        """
        self.agent_model = "openai"
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.oai_client = OpenAI(api_key=os.getenv("OPENAI"))
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC"))
        self.system_prompt = get_supervisor_system_prompt()

        self.oai_planner_tool = [
            {
                "type": "function",
                "function": {
                    "name": "plan_generator",
                    "description": "Generate a plan for an AI agent, given a prompt",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "plan": {
                                "type": "array",
                                "description": "an array of plans",
                                "items": {"type": "string"},
                            }
                        },
                        "required": ["plans"],
                    },
                },
            }
        ]

        self.planner_tool = [
            {
                "name": "plan_generator",
                "description": "Generate a plan for an AI agent, given a prompt",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "plan": {"type": "array", "description": "an array of plans"},
                    },
                    "required": ["plans"],
                },
            }
        ]

    def generate_plan(self, task):
        user_query = task
        if self.agent_model == "openai":
            response = self.oai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_query},
                ],
                tools=self.oai_planner_tool,
                tool_choice={
                    "type": "function",
                    "function": {"name": "plan_generator"},
                },
            )
            # print("Got response from OpenAI API")
            # print(response)
        else:
            response = self.client.beta.tools.messages.create(
                model="claude-3-opus-20240229",  # Choose the appropriate model for your use case
                messages=[{"role": "user", "content": self.system_prompt + user_query}],
                temperature=0,  # Adjust based on desired creativity
                max_tokens=1024,  # Adjust based on how detailed the response needs to be
                tools=self.planner_tool,
            )
        return response

    def parse_chat_response_to_subtasks(self, chat_response):
        if self.agent_model == "openai":
            first_tool_call = chat_response.choices[0].message.tool_calls[0]
            function_arguments = first_tool_call.function.arguments
            arguments_json = json.loads(function_arguments)
            plan = arguments_json["plan"]
        else:
            plan = [p for p in chat_response.content[1].input["plans"]]

        final_plans = []
        for plan_item in plan:
            subtasks = []
            if isinstance(plan_item, dict) and "plan" in plan_item:
                for step in plan_item["plan"]:
                    subtasks.append({"Subtask": step})
            elif isinstance(plan_item, dict) and "Subtask" in plan_item:
                if (
                    isinstance(plan_item["Subtask"], dict)
                    and "plan" in plan_item["Subtask"]
                ):
                    for step in plan_item["Subtask"]["plan"]:
                        subtasks.append({"Subtask": step})
                else:
                    subtasks.append(plan_item)
            else:
                subtasks.append({"Subtask": plan_item})
            final_plans.append(subtasks)

        return final_plans

    def run(self, user_id, run_id, task, provider):
        if task:
            try:
                print("Running agent...")
                agent_plan = self.generate_plan(task)
                plans = self.parse_chat_response_to_subtasks(agent_plan)
                print("\n")
                plan_statement = ""
                for idx, plan in enumerate(plans):
                    for sub_idx, subtask in enumerate(plan):
                        plan_statement += f"{subtask['Subtask']}\n"
                    plan_statement += "\n"
                print(plan_statement)

                worker = Worker(
                    user_id,
                    run_id,
                    user_query=task,
                    plan=plan_statement,
                    worker_number=1,
                    provider=provider,
                )

                worker_result = worker.run()
                return worker_result

            except Exception as e:
                print(
                    f"An error occurred in the Supervisor: {str(e)} on line {e.__traceback__.tb_lineno}"
                )
                traceback.print_exc()
                return "An error occurred while running the agent."
        else:
            print("No task chosen. Please run the command again with a valid task.")
