from git import Repo
import re
from typing import List

class ReadOnlyGitClient:
    def __init__(self, repo_url_or_path: str, local_path: str = None):
        """
        Initializes the client. Clones if a local path is provided, otherwise opens a local repo.
        """
        if local_path:
            self.repo = Repo.clone_from(repo_url_or_path, local_path)
        else:
            self.repo = Repo(repo_url_or_path)

    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.repo.close()    

    def list_branches(self, remote: bool = False) -> List:
        """
        Lists the local or remote branches.
        """
        if remote:
            return [ref.name for ref in self.repo.remotes.origin.refs]
        return [head.name for head in self.repo.heads]

    def list_tags(self) -> List:
        """
        Lists the tags available in the repository.
        """
        return [tag.name for tag in self.repo.tags]

    def list_commits(self, branch: str = None, max_count: int = None) -> List:
        """
        Lists the commits of a branch or the HEAD.
        """
        rev = branch or 'HEAD'
        commits = list(self.repo.iter_commits(rev, max_count=max_count))
        return [commit.hexsha for commit in commits]

    def get_commit(self, sha: str) ->str:
        """
        Retrieves a commit object by its SHA.
        """
        return self.repo.commit(sha)

    def get_latest_commit(self, branch: str = 'master'):
        """
        Retrieves the SHA of the latest commit on a branch.
        """
        return self.repo.commit(branch).hexsha

    def get_file_contents(self, filepath: str, sha: str = None) -> str:
        """
        Retrieves the content of a file at a given commit.
        """
        commit = self.repo.commit(sha) if sha else self.repo.head.commit
        blob = commit.tree / filepath
        return blob.data_stream.read().decode('utf-8')

    def get_diff(self, sha1: str, sha2: str):
        """
        Retrieves the diff between two commits.
        """
        return self.repo.git.diff(sha1, sha2)
    
    def get_last_diff(self, branch: str = 'main') -> str:
        """
        Returns the diff between the last two commits on a given branch.
        """
        commits = self.list_commits(branch=branch, max_count=2)
        if len(commits) < 2:
            raise ValueError("Not enough commits to generate a diff.")
        sha1, sha2 = commits[1], commits[0]
        return self.get_diff(sha1, sha2)

    def search_files(self, pattern: str, sha: str = None) -> List:
        """
        Searches for files by regex in the commit's tree.
        """
        commit = self.repo.commit(sha) if sha else self.repo.head.commit
        regex = re.compile(pattern)
        return [blob.path for blob in commit.tree.traverse() if blob.type == 'blob' and regex.search(blob.path)]

    def get_tree(self, sha: str = None) -> List:
        """
        Lists all the files in the repository at a given commit.
        """
        commit = self.repo.commit(sha) if sha else self.repo.head.commit
        return [blob.path for blob in commit.tree.traverse() if blob.type == 'blob']
