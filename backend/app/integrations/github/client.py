import httpx

from app.integrations.github.exceptions import GitHubRepositoryNotFoundError


class GitHubClient:
    """
    Small client responsible for communicating with the GitHub REST API.

    GitHub-specific HTTP details stay here so routes and services do not
    need to know how GitHub requests are made.
    """

    BASE_URL = "https://api.github.com"

    def __init__(self) -> None:
        self.timeout = httpx.Timeout(10.0)

    async def get_repository(
        self,
        owner: str,
        repository: str,
    ) -> dict:
        """
        Fetch basic repository metadata from GitHub.

        Heavy response mapping and error handling will be improved
        after the first working integration is verified.
        """

        url = f"{self.BASE_URL}/repos/{owner}/{repository}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)

        if response.status_code == 404:
            raise GitHubRepositoryNotFoundError(
                f"GitHub repository '{owner}/{repository}' was not found."
            )

        response.raise_for_status()

        return response.json()

    async def get_repository_languages(self, owner: str, repository: str) -> dict[str, int]:
        """
        Fetch the programming languages used in a GitHub repository.

        GitHub returns each language with the approximate number
        of bytes of code detected for that language
        """

        url = (
            f"{self.BASE_URL}/repos/"
            f"{owner}/{repository}/languages"

        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)

        if response.status_code == 404:
            raise GitHubRepositoryNotFoundError(
                f"GitHub repository '{owner}/{repository}' was not found."
            )

        response.raise_for_status()

        return response.json()

































