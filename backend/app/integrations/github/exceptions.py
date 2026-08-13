class GitHubAPIError(Exception):
    """Base error for GitHub API integration failures."""


class GitHubRepositoryNotFoundError(GitHubAPIError):
    """Raised when the requested GitHub repository does not exist."""