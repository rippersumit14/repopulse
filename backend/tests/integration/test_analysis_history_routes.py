from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.schemas.repository import (
    HealthScoreResponse,
    RepositoryCommitActivityResponse,
    RepositoryLanguagesResponse,
    RepositoryMetadataResponse,
)
from app.services.repository_analyzer import RepositoryAnalysisResult
from tests.conftest import register_and_login


def make_metadata() -> RepositoryMetadataResponse:
    now = datetime.now(timezone.utc)

    return RepositoryMetadataResponse(
        id=1,
        name="repo",
        full_name="owner/repo",
        description=None,
        repository_url="https://github.com/owner/repo",
        owner="owner",
        owner_avatar_url="https://example.com/avatar.png",
        stars=10,
        forks=2,
        watchers=10,
        open_issues=1,
        language="Python",
        topics=[],
        default_branch="main",
        license="MIT",
        is_fork=False,
        archived=False,
        visibility="public",
        created_at=now,
        updated_at=now,
        pushed_at=now,
    )


async def fake_analyze_repository(owner: str, repository: str) -> RepositoryAnalysisResult:
    return RepositoryAnalysisResult(
        metadata=make_metadata(),
        languages=RepositoryLanguagesResponse(total_bytes=100, languages=[]),
        activity=RepositoryCommitActivityResponse(
            total_recent_commits=6,
            commits_last_7_days=2,
            commits_last_30_days=6,
            last_commit_at=datetime.now(timezone.utc),
            days_since_last_commit=0,
            activity_level="medium",
        ),
        health_score=HealthScoreResponse(
            overall_score=80,
            activity_score=75,
            maintenance_score=85,
            reasons=["Recent activity detected."],
        ),
    )


def track_repository(client: TestClient, monkeypatch) -> tuple[str, int]:
    async def fake_get_repository(self, owner: str, repository: str) -> dict:
        metadata = make_metadata()
        return {
            "id": metadata.id,
            "name": metadata.name,
            "full_name": metadata.full_name,
            "description": metadata.description,
            "html_url": metadata.repository_url,
            "owner": {
                "login": metadata.owner,
                "avatar_url": metadata.owner_avatar_url,
            },
            "stargazers_count": metadata.stars,
            "forks_count": metadata.forks,
            "watchers_count": metadata.watchers,
            "open_issues_count": metadata.open_issues,
            "language": metadata.language,
            "topics": metadata.topics,
            "default_branch": metadata.default_branch,
            "license": {
                "spdx_id": metadata.license,
            },
            "fork": metadata.is_fork,
            "archived": metadata.archived,
            "visibility": metadata.visibility,
            "created_at": metadata.created_at.isoformat(),
            "updated_at": metadata.updated_at.isoformat(),
            "pushed_at": metadata.pushed_at.isoformat(),
        }

    monkeypatch.setattr(
        "app.integrations.github.client.GitHubClient.get_repository",
        fake_get_repository,
    )

    token = register_and_login(client, "history@example.com")
    response = client.post(
        "/api/v1/repositories/track",
        json={"repository_url": "https://github.com/owner/repo"},
        headers={"Authorization": f"Bearer {token}"},
    )

    return token, response.json()["id"]


def test_analyze_creates_snapshot_and_history(
    client: TestClient,
    monkeypatch,
) -> None:
    token, repository_id = track_repository(client, monkeypatch)

    monkeypatch.setattr(
        "app.api.v1.routes.repositories.analyze_repository",
        fake_analyze_repository,
    )

    analyze_response = client.post(
        f"/api/v1/repositories/{repository_id}/analyze",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert analyze_response.status_code == 200
    assert analyze_response.json()["health_score"]["overall_score"] == 80
    assert analyze_response.json()["snapshot_id"] > 0

    history_response = client.get(
        f"/api/v1/repositories/{repository_id}/history?range=7d",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert history_response.status_code == 200
    assert history_response.json()["range"] == "7d"
    assert len(history_response.json()["points"]) == 1

    history_30d_response = client.get(
        f"/api/v1/repositories/{repository_id}/history?range=30d",
        headers={"Authorization": f"Bearer {token}"},
    )
    history_12m_response = client.get(
        f"/api/v1/repositories/{repository_id}/history?range=12m",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert history_30d_response.status_code == 200
    assert history_30d_response.json()["range"] == "30d"
    assert history_12m_response.status_code == 200
    assert history_12m_response.json()["range"] == "12m"


def test_history_rejects_untracked_repository(
    client: TestClient,
    monkeypatch,
) -> None:
    _, repository_id = track_repository(client, monkeypatch)
    other_token = register_and_login(client, "other@example.com")

    response = client.get(
        f"/api/v1/repositories/{repository_id}/history?range=7d",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == 403
