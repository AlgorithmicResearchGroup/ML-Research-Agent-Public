import requests
import arxiv

semantic_scholar_tool_definitions = [
    {
        "name": "search_papers",
        "description": "Search for papers by search term. Use this tool to search for papers on Semantic Scholar with simple terms eg. 'Attention Mechanism'",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_paper_details",
        "description": "Get the details of a paper from Semantic Scholar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paper_id": {
                    "type": "string",
                    "description": "The Semantic Scholar paper ID.",
                },
            },
            "required": ["paper_id"],
        },
    },
    {
        "name": "get_paper_citations",
        "description": "Get the citations of a paper from Semantic Scholar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paper_id": {
                    "type": "string",
                    "description": "The Semantic Scholar paper ID.",
                },
            },
            "required": ["paper_id"],
        },
    },
    {
        "name": "download_paper",
        "description": "Download the pdf paper from Semantic Scholar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paper_id": {
                    "type": "string",
                    "description": "The Semantic Scholar paper ID",
                },
            },
            "required": ["paper_id"],
        },
    },
]


def structure_paper_output(query_response):
    text = []
    for paper in query_response:
        output = f"""
    title: {paper['title']}
    abstract: {paper['abstract']}
    paper_id: {paper['paper_id']}
    arxiv_id: {paper.get('arxiv_id', '')}
    -----------------------------------------------
    """
        text.append(output)

    output_string = " ".join(text)
    return output_string


class SemanticScholarAPI:
    def __init__(self):
        self.api_key = "qTasW7oQ5c5Mek9IF5To2a5MnT39zkqy1Z9oMLa6"
        self.base_url = "https://api.semanticscholar.org/graph/v1"

    def make_request(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        headers = {"x-api-key": self.api_key} if self.api_key else {}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Request failed with status code: {response.status_code}")

    def search_papers(self, query, limit=10):
        fields = "title,abstract,externalIds"
        params = {"query": query, "fields": fields, "limit": limit}
        response = self.make_request("paper/search", params)
        # print(f"here's the response in search_papers {response}")
        papers = []
        for paper in response["data"]:
            title = paper.get("title", "")
            abstract = paper.get("abstract", "")
            paper_id = paper.get("paperId", "")
            arxiv_id = paper.get("externalIds", {}).get("ArXiv", "None")
            papers.append(
                {
                    "title": title,
                    "abstract": abstract,
                    "paper_id": paper_id,
                    "arxiv_id": arxiv_id,
                }
            )

        return papers

    def get_paper_details(self, paper_id, fields=None):
        params = {"fields": fields}
        return self.make_request(f"paper/{paper_id}", params)

    def get_paper_url(self, paper_id):
        paper_details = self.get_paper_details(paper_id, fields="url")
        return paper_details.get("url", "")

    def get_paper_citations(self, paper_id, fields=None, limit=10):
        # params = {'fields': fields, 'limit': limit}
        return self.make_request(f"paper/{paper_id}/citations")

    def download_paper(self, arxiv_id):
        try:
            paper = next(arxiv.Search(id_list=[arxiv_id]).results())
            return paper.download_pdf()
        except StopIteration:
            return None

    def download_paper_by_paper_id(self, paper_id):
        paper_details = self.make_request(
            f"paper/{paper_id}", params={"fields": "externalIds"}
        )
        external_ids = paper_details.get("externalIds")
        print(f"Here are the external ids {external_ids}")
        if external_ids and "ArXiv" in external_ids:
            arxiv_id = external_ids["ArXiv"]
            filename = self.download_paper(arxiv_id)
            if filename:
                return filename
            else:
                return None
        else:
            return None


def search_papers(arguments):
    """
    This function is used to search for papers on arXiv.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        query = arguments["query"]
    else:
        query = arguments

    try:
        semantic_scholar_api = SemanticScholarAPI()
        result = semantic_scholar_api.search_papers(query, limit=10)
        result = structure_paper_output(result)
        return {
            "tool": "search_papers",
            "status": "success",
            "attempt": f" You searched for {query}",
            "stdout": f"Here are the search results: {result}",
            "stderr": "",
        }
    except Exception as e:
        return {
            "tool": "search_papers",
            "status": "failure",
            "attempt": f" You tried to search for {query}",
            "stdout": "",
            "stderr": str(e),
        }


def get_paper_details(arguments):
    """
    This function is used to get the details of a paper from arXiv.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        paper_id = arguments["paper_id"]
    else:
        paper_id = arguments

    try:
        semantic_scholar_api = SemanticScholarAPI()
        paper_details = semantic_scholar_api.get_paper_details(
            paper_id, fields="title,year,abstract,authors.name"
        )
        return {
            "tool": "get_paper_details",
            "status": "success",
            "attempt": f" You looked at {paper_id}",
            "stdout": f"Here are the paper details: {paper_details}",
            "stderr": "",
        }
    except Exception as e:
        return {
            "tool": "get_paper_details",
            "status": "failure",
            "attempt": f" You tried to look at {paper_id}",
            "stdout": "",
            "stderr": str(e),
        }


def get_paper_citations(arguments):
    """
    This function is used to get the citations of a paper from arXiv.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        paper_id = arguments["paper_id"]
    else:
        paper_id = arguments

    try:
        semantic_scholar_api = SemanticScholarAPI()
        result = semantic_scholar_api.get_paper_citations(
            paper_id, fields="title,year,abstract,authors.name"
        )
        return {
            "tool": "get_paper_citations",
            "status": "success",
            "attempt": f" You looked at {paper_id}",
            "stdout": f"Here are the citations: {result}",
            "stderr": "",
        }
    except Exception as e:
        return {
            "tool": "get_paper_citations",
            "status": "failure",
            "attempt": f" You tried to look at {paper_id}",
            "stdout": "",
            "stderr": str(e),
        }


def download_paper(arguments):
    """
    This function is used to get the full text of a paper from arXiv.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        paper_id = arguments["paper_id"]
    else:
        paper_id = arguments

    try:
        semantic_scholar_api = SemanticScholarAPI()
        full_text = semantic_scholar_api.download_paper_by_paper_id(paper_id)
        return {
            "tool": "get_paper_full_text",
            "status": "success",
            "attempt": f" You looked at {paper_id}",
            "stdout": f"Here is the full text: {full_text}",
            "stderr": "",
        }
    except Exception as e:
        return {
            "tool": "get_paper_full_text",
            "status": "failure",
            "attempt": f" You tried to look at {paper_id}",
            "stdout": "",
            "stderr": str(e),
        }
