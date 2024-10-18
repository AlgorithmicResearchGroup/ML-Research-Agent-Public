import redis
from redis.commands.search.field import TagField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from sentence_transformers import SentenceTransformer

code_lookup_tool_deinitions = [
    {
        "name": "lookup_code",
        "description": "Lookup code snippets in a database.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
            },
            "required": ["query"],
        },
    },
]


class RedisCodeLookUp:
    def __init__(self):
        self.cache = {}
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index_name = "code"
        self.redis_db = redis.Redis(
            username="default",
            password="YVm2qhsQOlbP23Nt64lSSFi1CR5TfoG0",
            host="redis-19266.c239.us-east-1-2.ec2.redns.redis-cloud.com",
            port=19266,
        )

    def search_code(self, query):
        query_sentence = query
        vec = self.model.encode(query_sentence)
        query = (
            Query("*=>[KNN 20 @vector $vec as score]")
            .sort_by("score")
            .return_fields("id", "function_summary", "function")
            .paging(0, 10)
            .dialect(2)
        )
        query_params = {"vec": vec.astype(np.float32).tobytes()}
        results = self.redis_db.ft(self.index_name).search(query, query_params).docs
        return results


def lookup_code(arguments):
    """
    This function is used to look up code snippets in a database.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        query = arguments["query"]
    else:
        query = arguments

    try:
        redis_code_lookup = RedisCodeLookUp()
        result = redis_code_lookup.search_code(query)
        return {
            "tool": "lookup_code",
            "status": "success",
            "attempt": f" You searched for {query}",
            "stdout": f"Here are the search results: {result}",
            "stderr": "",
        }
    except Exception as e:
        return {
            "tool": "lookup_code",
            "status": "failure",
            "attempt": f" You tried to search for {query}",
            "stdout": "",
            "stderr": str(e),
        }
