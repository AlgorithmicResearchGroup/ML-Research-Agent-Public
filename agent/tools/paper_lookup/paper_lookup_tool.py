import redis
from redis.commands.search.field import TagField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from dotenv import load_dotenv
from agent.utils import structure_paper_output
from sentence_transformers import SentenceTransformer
from numpy import np

paper_lookup_tool_definitions = [
    {
        "name": "lookup_papers",
        "description": "Lookup papers in a database.",
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
    }
]


class RedisPaperLookUp:
    def __init__(self):
        self.cache = {}
        self.index_name = "papers"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.redis_db = redis.Redis(
            username="default",
            password="YVm2qhsQOlbP23Nt64lSSFi1CR5TfoG0",
            host="redis-19266.c239.us-east-1-2.ec2.redns.redis-cloud.com",
            port=19266,
        )

    def search_papers(self, query):
        query_sentence = query
        vec = self.model.encode(query_sentence)
        query = (
            Query("*=>[KNN 20 @vector $vec as score]")
            .sort_by("score")
            .return_fields("id", "title", "abstract")
            .paging(0, 10)
            .dialect(2)
        )
        query_params = {"vec": vec.astype(np.float32).tobytes()}
        results = self.redis_db.ft(self.index_name).search(query, query_params).docs
        return results


def lookup_papers(arguments):
    """
    This function is used to look up papers in a database.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        query = arguments["query"]
    else:
        query = arguments

    try:
        redis_paper_lookup = RedisPaperLookUp()
        result = redis_paper_lookup.search_papers(query)
        result = structure_paper_output(result)
        return {
            "tool": "lookup_papers",
            "status": "success",
            "attempt": f" You searched for {query}",
            "stdout": f"Here are the search results: {result}",
            "stderr": "",
        }
    except Exception as e:
        return {
            "tool": "lookup_papers",
            "status": "failure",
            "attempt": f" You tried to search for {query}",
            "stdout": "",
            "stderr": str(e),
        }
