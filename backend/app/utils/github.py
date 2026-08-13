def extract_github_repository(repository_url: str) -> tuple[str, str]:
    """
    Extract the repo owner and repository name
    from a normalized GitHub Repo URL.
    """

    github_prefix = "https://github.com/"

    #Remove the GitHub domain.
    repository_path = repository_url.removeprefix(github_prefix)

    #Split "owner/repo" into two values
    owner, repository = repository_path.split("/", maxsplit=1)

    return owner, repository


