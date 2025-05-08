from Clients.read_only_git_client import ReadOnlyGitClient
from agents.CrewAgents.crew_agent import CrewAIAgent

import re
import os

from typing import List
from crewai.tools import tool

class GitRepoAnalysisAgent(CrewAIAgent):
    def __init__(self, model: str = "gemini/gemini-1.5-flash-002"):
        self.role = "Git Repository Analyst"
        self.goal = "Analyze the history, structure, and content of a Git repository."
        self.instructions = "Use dedicated Git tools to accurately answer queries."
        self.backstory = "Expert in code exploration of Public Git repos."

        super().__init__(model)

        self.local_repo = "temp_uploads"
        self.initial_message = True

    def _create_tools(self) -> List:
        @tool("clone_repo")
        def clone_repo_tool(repo_url: str) -> str:
            """
            Clone a remote repository into the temp_uploads directory.
            Input: repo_url (str).
            Output: cloned local path (str).
            """
            name = self.get_repo_name(repo_url)
            local_path = f"temp_uploads/{name}"
            
            if not os.path.exists(local_path):
                os.makedirs(local_path, exist_ok=True)
                client = ReadOnlyGitClient(repo_url, local_path)
            else:
                return f"There is already a clone in current repo, use repo_path ={local_path} to access it"
            
            return f"Cloned to {client.repo.working_dir}"

        @tool("list_branches")
        def list_branches_tool(repo_path: str, remote: bool = False) -> str:
            """
            List local or remote branches.
            Input: repo_path (str), remote (bool).
            Output: list of branches (str).
            """
            with ReadOnlyGitClient(repo_path) as client:
                branches = client.list_branches(remote=remote)
            return "\n".join(branches)

        @tool("list_tags")
        def list_tags_tool(repo_path: str) -> str:
            """
            List all tags in the repository.
            Input: repo_path (str).
            Output: list of tags (str).
            """
            with ReadOnlyGitClient(repo_path) as client:
                return "\n".join(client.list_tags())

        @tool("list_commits")
        def list_commits_tool(repo_path: str, branch: str = None, max_count: int = None) -> str:
            """
            List commits of a specific branch.
            Input: repo_path (str), branch (str, optional), max_count (int, optional).
            Output: list of commit SHAs (str).
            """
            with ReadOnlyGitClient(repo_path) as client:
                commits = client.list_commits(branch=branch, max_count=max_count)
            return "\n".join(commits)

        @tool("get_latest_commit")
        def get_latest_commit_tool(repo_path: str, branch: str = 'main') -> str:
            """
            Retrieve the SHA of the latest commit in a branch.
            Input: repo_path (str), branch (str, optional).
            Output: SHA (str).
            """
            with ReadOnlyGitClient(repo_path) as client:
                return client.get_latest_commit(branch=branch)

        @tool("get_file_contents")
        def get_file_contents_tool(repo_path: str, filepath: str, sha: str = None) -> str:
            """
            Read the contents of a file at a given commit.
            Input: repo_path (str), filepath (str), sha (str, optional).
            Output: file contents (str).
            """
            with ReadOnlyGitClient(repo_path) as client:
                return client.get_file_contents(filepath, sha)

        @tool("get_diff")
        def get_diff_tool(repo_path: str, sha1: str, sha2: str) -> str:
            """
            Get the diff between two commits.
            Input: repo_path (str), sha1 (str), sha2 (str)
            Output: diff (str).
            """
            with ReadOnlyGitClient(repo_path) as client:
                return client.get_diff(sha1, sha2)

        @tool("search_files")
        def search_files_tool(repo_path: str, pattern: str, sha: str = None) -> str:
            """
            Search files by regex pattern.
            Input: repo_path (str), pattern (str), sha (str, optional).
            Output: list of matching files (str).
            """
            with ReadOnlyGitClient(repo_path) as client:
                files = client.search_files(pattern, sha)
            return "\n".join(files)

        @tool("get_tree")
        def get_tree_tool(repo_path: str, sha: str = None) -> str:
            """
            List all files at a given commit.
            Input: repo_path (str), sha (str, optional).
            Output: list of files (str).
            """
            with ReadOnlyGitClient(repo_path) as client:
                return "\n".join(client.get_tree(sha))

        @tool("get_last_diff")
        def get_last_diff_tool(repo_path: str, branch: str="main") -> str:
            """
            Get the the diff from the last commit
            Inputs:  branch (str, optional).
            Output: last diffs (str)
            """
            with ReadOnlyGitClient(repo_path) as client:
                return client.get_last_diff(branch)

        return [
            clone_repo_tool,
            list_branches_tool,
            list_tags_tool,
            list_commits_tool,
            get_latest_commit_tool,
            get_file_contents_tool,
            get_diff_tool,
            search_files_tool,
            get_tree_tool,
            get_last_diff_tool
        ]
    def get_repo_name(self, url: str)-> str:
        """
        Returns the name of the repo from the git url
        """
        pattern = r'(?<=/)[^/]+(?=\.git$)'
        match = re.search(pattern, url)
        if match:
            return match.group(0)
        else:
            return None
