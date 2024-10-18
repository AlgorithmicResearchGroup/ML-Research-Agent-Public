papers_with_code_tool_definitions = [
    {
        "name": "search_papers_with_code",
        "description": "Search for machine learning papers on Papers with Code. Use this tool to find papers related to a specific topic or keyword.",
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
    {
        "name": "get_paper_details_pwc",
        "description": "Get detailed information about a specific paper from Papers with Code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paper_id": {
                    "type": "string",
                    "description": "The Papers with Code paper ID.",
                },
            },
            "required": ["paper_id"],
        },
    },
    {
        "name": "get_code_links",
        "description": "Retrieve code repositories associated with a specific paper.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paper_id": {
                    "type": "string",
                    "description": "The Papers with Code paper ID.",
                },
            },
            "required": ["paper_id"],
        },
    },
    # Add more tool definitions as needed
]

import requests

def search_papers_with_code(arguments):
    """
    Search for papers on Papers with Code.
    """
    if isinstance(arguments, dict):
        query = arguments["query"]
    else:
        query = arguments

    try:
        url = "https://paperswithcode.com/api/v1/papers/"
        params = {"q": query}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract relevant information
        papers = data.get("results", [])
        results = []
        for paper in papers[:10]:  # Limit to top 10 results
            title = paper.get("title")
            abstract = paper.get("abstract", "No abstract available.")
            paper_url = paper.get("url_abs")
            paper_id = paper.get("id")
            results.append(f"Title: {title}\nPaper ID: {paper_id}\nURL: {paper_url}\n")

        output = "\n".join(results)
        return {
            "tool": "search_paperswithcode",
            "status": "success",
            "attempt": f" You searched for '{query}'",
            "stdout": f"Here are the top search results:\n{output}",
            "stderr": "",
        }
    except Exception as e:
        return {
            "tool": "search_paperswithcode",
            "status": "failure",
            "attempt": f" You tried to search for '{query}'",
            "stdout": "",
            "stderr": str(e),
        }


def get_paper_details_pwc(arguments):
    """
    Get detailed information about a specific paper from Papers with Code.
    """
    if isinstance(arguments, dict):
        paper_id = arguments["paper_id"]
    else:
        paper_id = arguments

    try:
        url = f"https://paperswithcode.com/api/v1/papers/{paper_id}/"
        response = requests.get(url)
        response.raise_for_status()
        paper_details = response.json()

        # Extract relevant information
        title = paper_details.get("title")
        abstract = paper_details.get("abstract", "No abstract available.")
        authors = paper_details.get("authors", [])
        url_pdf = paper_details.get("url_pdf")
        url_abs = paper_details.get("url_abs")
        tasks = [task['name'] for task in paper_details.get("tasks", [])]

        output = f"""
        Title: {title}
        Authors: {', '.join(authors)}
        Abstract: {abstract}
        PDF URL: {url_pdf}
        Abstract URL: {url_abs}
        Tasks: {', '.join(tasks)}
        """

        return {
            "tool": "get_paper_details_pwc",
            "status": "success",
            "attempt": f" You retrieved details for paper ID '{paper_id}'",
            "stdout": output,
            "stderr": "",
        }
    except Exception as e:
        return {
            "tool": "get_paper_details_pwc",
            "status": "failure",
            "attempt": f" You tried to retrieve details for paper ID '{paper_id}'",
            "stdout": "",
            "stderr": str(e),
        }



def get_code_links_pwc(arguments):
    """
    Retrieve code repositories associated with a specific paper.
    """
    if isinstance(arguments, dict):
        paper_id = arguments["paper_id"]
    else:
        paper_id = arguments

    try:
        url = f"https://paperswithcode.com/api/v1/papers/{paper_id}/repositories/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        repositories = data.get("results", [])
        if not repositories:
            output = "No code repositories found for this paper."
        else:
            results = []
            for repo in repositories:
                repo_url = repo.get("url")
                repo_name = repo.get("name")
                results.append(f"Repository Name: {repo_name}\nURL: {repo_url}\n")

            output = "\n".join(results)

        return {
            "tool": "get_code_links",
            "status": "success",
            "attempt": f" You retrieved code links for paper ID '{paper_id}'",
            "stdout": output,
            "stderr": "",
        }
    except Exception as e:
        return {
            "tool": "get_code_links",
            "status": "failure",
            "attempt": f" You tried to retrieve code links for paper ID '{paper_id}'",
            "stdout": "",
            "stderr": str(e),
        }