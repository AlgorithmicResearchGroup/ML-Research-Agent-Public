import requests
import os
from bs4 import BeautifulSoup

internet_search_tool_definitions = [
    {
        "name": "search_the_internet",
        "description": "Search the internet for information on a given query using the YOU API. Use this tool to perform general web searches when you need current or general information.",
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
        "name": "navigate_to_website",
        "description": "Navigate to a specific website and extract its main content. Use this tool when you need to visit a particular URL and retrieve information from it.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the website to navigate to.",
                },
            },
            "required": ["url"],
        },
    },
]


def search_the_internet(arguments):
    """
    This function searches the internet using the YOU API.
    """
    if isinstance(arguments, dict):
        query = arguments.get("query")
    else:
        query = arguments

    if not query:
        return {
            "tool": "search_the_internet",
            "status": "failure",
            "attempt": "No query provided.",
            "stdout": "",
            "stderr": "Query parameter is missing.",
        }

    try:
        api_key = os.getenv("YOU_API_KEY")
        if not api_key:
            return {
                "tool": "search_the_internet",
                "status": "failure",
                "attempt": f"You tried to search for '{query}'",
                "stdout": "",
                "stderr": "YOU API key not found in environment variables.",
            }

        headers = {"X-API-Key": api_key}
        params = {"query": query}
        response = requests.get("https://api.ydc-index.io/search", headers=headers, params=params)
        response.raise_for_status()
        search_results = response.json()

        # Process the search results
        hits = search_results.get("hits", [])
        results = []
        for hit in hits[:5]:  # Limit to top 5 results
            title = hit.get("title", "No Title")
            description = hit.get("description", "")
            url = hit.get("url", "")
            snippets = hit.get("snippets", [])
            snippet_text = "\n".join(snippets)
            results.append(
                f"Title: {title}\nDescription: {description}\nURL: {url}\nSnippets:\n{snippet_text}\n{'-'*50}"
            )

        output = "\n".join(results)
        return {
            "tool": "search_the_internet",
            "status": "success",
            "attempt": f"You searched for '{query}'",
            "stdout": f"Here are the top search results:\n{output}",
            "stderr": "",
        }
    except Exception as e:
        return {
            "tool": "search_the_internet",
            "status": "failure",
            "attempt": f"You tried to search for '{query}'",
            "stdout": "",
            "stderr": str(e),
        }


def navigate_to_website(arguments):
    """
    This function navigates to a specific website and extracts its main content.
    """
    if isinstance(arguments, dict):
        url = arguments.get("url")
    else:
        url = arguments

    if not url:
        return {
            "tool": "navigate_to_website",
            "status": "failure",
            "attempt": "No URL provided.",
            "stdout": "",
            "stderr": "URL parameter is missing.",
        }

    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the main content (this is a simple example and might need adjustment)
        main_content = soup.find('main') or soup.find('body')
        
        if main_content:
            # Remove script and style elements
            for script in main_content(["script", "style"]):
                script.decompose()
            
            text = main_content.get_text(separator='\n', strip=True)
        else:
            text = "Could not extract main content."

        return {
            "tool": "navigate_to_website",
            "status": "success",
            "attempt": f"You navigated to '{url}'",
            "stdout": f"Content from {url}:\n\n{text[:1000]}...",  # Truncate to first 1000 characters
            "stderr": "",
        }
    except Exception as e:
        return {
            "tool": "navigate_to_website",
            "status": "failure",
            "attempt": f"You tried to navigate to '{url}'",
            "stdout": "",
            "stderr": str(e),
        }
