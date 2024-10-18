import os
import requests
import base64


github_tool_definitions = [
    {
        "name": "github_get_readme",
        "description": "Get the readme file from a github repo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_url": {
                    "type": "string",
                    "description": "The URL of the github repo.",
                },
            },
            "required": ["repo_url"],
        },
    },
    {
        "name": "github_list_files",
        "description": "List all files in a github repo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_url": {
                    "type": "string",
                    "description": "The URL of the github repo.",
                },
            },
            "required": ["repo_url"],
        },
    },
    {
        "name": "github_get_file_code",
        "description": "Get the code from a file in a github repo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_url": {
                    "type": "string",
                    "description": "The URL of the github repo.",
                },
                "file_path": {
                    "type": "string",
                    "description": "The path to the file in the github repo. eg. 'src/main.py'",
                },
            },
            "required": ["repo_url", "file_path"],
        },
    },
]


class GitHubRepoActor:
    def __init__(self, repo_url, access_token=None):
        self.access_token = os.getenv("GITHUB_ACCESS_TOKEN")
        self.repo_url = repo_url
        self.access_token = self.access_token
        self.api_url = self.get_api_url()

    def get_api_url(self):
        # Extract the username and repository name from the repo URL
        parts = self.repo_url.split("/")
        username = parts[-2]
        repo_name = parts[-1]
        return f"https://api.github.com/repos/{username}/{repo_name}"

    def make_request(self, endpoint):
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Token {self.access_token}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Request failed with status code: {response.status_code}")

    def retrieve_contents(self, path):
        contents = self.make_request(f"contents/{path}")
        file_list = []
        for item in contents:
            if item["type"] == "file":
                file_list.append(item["path"])
            elif item["type"] == "dir":
                file_list.extend(self.retrieve_contents(item["path"]))
        return file_list

    def get_readme(self):
        try:
            readme_data = self.make_request("readme")
            readme_content = base64.b64decode(readme_data["content"]).decode("utf-8")
            return {
                "tool": "get_readme",
                "status": "success",
                "attempt": f" You looked at {self.get_api_url()}",
                "stdout": f"Here is the readme content: {readme_content}",
                "stderr": "",
            }
        except Exception as e:
            return {
                "tool": "get_readme",
                "status": "failure",
                "attempt": f" You tried to look at {self.get_api_url()}",
                "stdout": "",
                "stderr": str(e),
            }

    def list_files(self):
        try:
            file_list = self.retrieve_contents("")
            file_list = "\n".join(file_list)
            return {
                "tool": "list_files",
                "status": "success",
                "attempt": f" You looked at {self.get_api_url()}",
                "stdout": f"Here is the list of files: {file_list}",
                "stderr": "",
            }
        except Exception as e:
            return {
                "tool": "list_files",
                "status": "failure",
                "attempt": f" You tried to look at {self.get_api_url()}",
                "stdout": "",
                "stderr": str(e),
            }

    def get_file_code(self, file_path):
        try:
            file_contents = self.make_request(f"contents/{file_path}")
            file_code = base64.b64decode(file_contents["content"]).decode("utf-8")
            return {
                "tool": "get_file_code",
                "status": "success",
                "attempt": f" You looked at {file_path}",
                "stdout": f"Here is the code: {file_code}",
                "stderr": "",
            }
        except Exception as e:
            return {
                "tool": "get_file_code",
                "status": "failure",
                "attempt": f" You tried to look at {file_path}",
                "stdout": "",
                "stderr": str(e),
            }


def github_get_readme(arguments):  # get the readme file from a github repo
    """
    This function is used to get the readme file from a github repo.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        repo_url = arguments["repo_url"]
    else:
        repo_url = arguments

    github_actor = GitHubRepoActor(repo_url)
    result = github_actor.get_readme()
    return result


def github_list_files(arguments):  # list all files in a github repo
    """
    This function is used to list all files in a github repo.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        repo_url = arguments["repo_url"]
    else:
        repo_url = arguments

    github_actor = GitHubRepoActor(repo_url)
    result = github_actor.list_files()
    return result


def github_get_file_code(arguments):  # get the code from a file in a github repo
    """
    This function is used to get the code from a file in a github repo.
    Use this function to run the code you need to complete the task.
    """
    if isinstance(arguments, dict):
        repo_url = arguments["repo_url"]
        file_path = arguments["file_path"]
    else:
        repo_url = arguments[0]
        file_path = arguments[1]

    github_actor = GitHubRepoActor(repo_url)
    result = github_actor.get_file_code(file_path)
    return result
