import os
from openai import OpenAI
from agent.utils import count_tokens
from agent.utils import anthropic_to_openai
import json
import tiktoken


class OpenAIModel:
    def __init__(self, system_prompt, all_tools):
        self.system_prompt = system_prompt
        self.oai_client = OpenAI(api_key=os.getenv("OPENAI"))
        self.all_tools = all_tools
        self.max_tokens = 124000   # Maximum tokens for GPT-4
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def encode_text(self, text):
        # Allow all special tokens to be encoded as normal text
        return self.encoding.encode(text, disallowed_special=())

    def decode_tokens(self, tokens):
        return self.encoding.decode(tokens)

    def truncate_prompt(self, prompt, max_tokens):
        tokens = self.encode_text(prompt)
        if len(tokens) <= max_tokens:
            return prompt
        return self.decode_tokens(tokens[:max_tokens])

    def generate_response(self, prompt):
        system_prompt_tokens = len(self.encode_text(self.system_prompt))
        available_tokens = (
            self.max_tokens - system_prompt_tokens - 100
        )  # Reserve some tokens for the response

        truncated_prompt = self.truncate_prompt(prompt, available_tokens)
        prompt_tokens = len(self.encode_text(truncated_prompt))

        response = self.oai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": truncated_prompt},
            ],
            tools=[anthropic_to_openai(tool) for tool in self.all_tools],
        )
        response_data, response_tokens = self.get_openai_response(response)
        total_tokens = system_prompt_tokens + prompt_tokens + response_tokens

        return response_data, total_tokens, prompt_tokens, response_tokens

    def get_openai_response(self, response):
        # Initialize default response data
        response_data = None
        # Check if the response has 'choices' and if the first choice has 'tool_calls'
        if hasattr(response, "choices") and response.choices:
            for choice in response.choices:
                if (
                    hasattr(choice, "finish_reason")
                    and choice.finish_reason == "tool_calls"
                ):
                    response_data = choice.message.tool_calls[0].function.arguments
                    response_tokens = count_tokens(response_data, "cl100k_base")
                    response_data = json.loads(response_data)
                    return response_data, response_tokens
                else:
                    print("No tool calls found in this choice.")
                    response_data = choice.message.content
                    response_tokens = count_tokens(response_data, "cl100k_base")
                    return response_data, response_tokens
            else:
                print("No choices found in the response.")
                return response_data, 0
