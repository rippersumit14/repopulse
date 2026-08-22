from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.integrations.github.exceptions import GitHubRepositoryNotFoundError
from tests.conftest import register_and_login


def repository_payload() -> dict:
    return {
        "id": 100,
        "name": "repo",
        "full_name": "owner/repo",
        "description": "A test repository",
        "html_url": "https://github.com/owner/repo",
        "owner": {
            "login": "owner",
            "avatar_url": "https://example.com/avatar.png",
        },
        "stargazers_count": 10,
        "forks_count": 2,
        "watchers_count": 10,
        "open_issues_count": 1,
        "language": "Python",
        "topics": ["api"],
        "default_branch": "main",
        "license": {
            "spdx_id": "MIT",
        },
        "fork": False,
        "archived": False,
        "visibility": "public",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "pushed_at": datetime.now(timezone.utc).isoformat(),
    }


def test_repository_validation_normalizes_urls(client: TestClient) -> None:
    response = client.post(
        "/api/v1/repositories/validate",
        json={"repository_url": " https://github.com/owner/repo.git/ "},
    )

    assert response.status_code == 200
    assert response.json() == {
        "repository_url": "https://github.com/owner/repo",
        "valid": True,
    }


def test_repository_validation_rejects_invalid_host(client: TestClient) -> None:
    response = client.post(
        "/api/v1/repositories/validate",
        json={"repository_url": "https://gitlab.com/owner/repo"},
    )

    assert response.status_code == 422


def test_metadata_uses_mocked_github_success(client: TestClient, monkeypatch) -> None:
    async def fake_get_repository(self, owner: str, repository: str) -> dict:
        return repository_payload()

    monkeypatch.setattr(
        "app.integrations.github.client.GitHubClient.get_repository",
        fake_get_repository,
    )

    response = client.post(
        "/api/v1/repositories/metadata",
        json={"repository_url": "https://github.com/owner/repo"},
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "owner/repo"


def test_metadata_maps_github_404(client: TestClient, monkeypatch) -> None:
    async def fake_get_repository(self, owner: str, repository: str) -> dict:
        raise GitHubRepositoryNotFoundError("missing")

    monkeypatch.setattr(
        "app.integrations.github.client.GitHubClient.get_repository",
        fake_get_repository,
    )

    response = client.post(
        "/api/v1/repositories/metadata",
        json={"repository_url": "https://github.com/owner/missing"},
    )

    assert response.status_code == 404


def test_tracking_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/api/v1/repositories/track",
        json={"repository_url": "https://github.com/owner/repo"},
    )

    assert response.status_code == 401


def test_user_owned_tracking_and_duplicate_prevention(
    client: TestClient,
    monkeypatch,
) -> None:
    async def fake_get_repository(self, owner: str, repository: str) -> dict:
        return repository_payload()

    monkeypatch.setattr(
        "app.integrations.github.client.GitHubClient.get_repository",
        fake_get_repository,
    )

    first_token = register_and_login(client, "first@example.com")
    second_token = register_and_login(client, "second@example.com")

    first_response = client.post(
        "/api/v1/repositories/track",
        json={"repository_url": "https://github.com/owner/repo"},
        headers={"Authorization": f"Bearer {first_token}"},
    )
    duplicate_response = client.post(
        "/api/v1/repositories/track",
        json={"repository_url": "https://github.com/owner/repo"},
        headers={"Authorization": f"Bearer {first_token}"},
    )
    second_response = client.post(
        "/api/v1/repositories/track",
        json={"repository_url": "https://github.com/owner/repo"},
        headers={"Authorization": f"Bearer {second_token}"},
    )

    assert first_response.status_code == 200
    assert duplicate_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["id"] == duplicate_response.json()["id"]
    assert first_response.json()["id"] == second_response.json()["id"]
