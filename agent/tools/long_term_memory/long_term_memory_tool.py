from agent.memory import AgentMemory

long_term_memory_tool_definitions = [
    {
        "name": "long_term_memory",
        "description": "Access the agent's long-term memory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search in the long-term memory.",
                },
                "run_id": {
                    "type": "integer",
                    "description": "The current run ID to contextualize the search.",
                },
            },
            "required": ["query", "run_id"],
        },
    },
]


class LongTermMemory:
    def __init__(self):
        self.memory = AgentMemory()

    def access_memory(self, query, run_id):
        try:
            memories = self.memory.search_memories(query, run_id)
            return {
                "tool": "long_term_memory",
                "status": "success",
                "attempt": f"You searched the long-term memory for: {query}",
                "stdout": f"Here are the relevant memories:\n{memories}",
                "stderr": "",
            }
        except Exception as e:
            return {
                "tool": "long_term_memory",
                "status": "failure",
                "attempt": f"You tried to search the long-term memory for: {query}",
                "stdout": "",
                "stderr": str(e),
            }


def use_long_term_memory(arguments):
    """
    This function is used to access the agent's long-term memory.
    Use this function to search for relevant information from past experiences.
    """
    if isinstance(arguments, dict):
        query = arguments["query"]
        run_id = arguments["run_id"]
    else:
        query, run_id = arguments

    long_term_memory = LongTermMemory()
    result = long_term_memory.access_memory(query, run_id)
    return result
