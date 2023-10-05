import secrets
from fastapi import status
import pytest


def test_authorization_endpoint(api_client):
    response = api_client.get("/authorize")
    response_data = response.json()
    assert response.status_code == 200
    assert "authorization_url" in response_data
    authorization_url: str = response_data.get("authorization_url")
    assert authorization_url.startswith("https://slack.com/oauth/v2/authorize?")
    assert "client_id" in authorization_url
    assert "redirect_uri" in authorization_url


@pytest.mark.asyncio
async def test_get_authorization_token(mock_async_post, api_client):
    random_token = secrets.token_urlsafe(20)
    mock_async_post.return_value.__aenter__.return_value.status = 200
    mock_async_post.return_value.__aenter__.return_value.json.return_value = {
        "ok": True,
        "authed_user": {"id": "1", "access_token": random_token},
        "team": {},
    }
    response = api_client.get(f"/post-authorize?code=1234")
    assert response.status_code == 200
    assert response.json()["access_token"] == random_token


def test_get_authorization_token_without_code(api_client):
    response = api_client.get(f"/post-authorize")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_users_endpoint(mock_async_get, api_client):
    mock_async_get.return_value.__aenter__.return_value.status = 200
    mock_async_get.return_value.__aenter__.return_value.json.return_value = {
        "ok": True,
        "members": [
            {
                "id": "1",
                "team_id": "123",
                "profile": {
                    "first_name": "Ray",
                    "last_name": "Ray",
                    "real_name": "Ray",
                    "email": "ray@example.com",
                },
            },
        ],
        "response_metadata": {},
    }
    response = api_client.get(
        "/get-users?page_token=123", headers={"auth-token": "Bearer sample-token"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data.get("users"), list)
    assert response_data.get("page_token") == "123"


def test_get_users_endpoint_without_auth_token(api_client):
    response = api_client.get("/get-users", headers={"some-header": "some-values"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "connection_verified_status",
    [True, False],
)
async def test_verify_connection(
    mock_async_post, api_client, connection_verified_status
):
    mock_async_post.return_value.__aenter__.return_value.status = 200
    mock_async_post.return_value.__aenter__.return_value.json.return_value = {
        "ok": connection_verified_status
    }

    response = api_client.get("/verify-connection?code=1234")
    response_data = response.json()

    assert response.status_code == 200
    assert response_data.get("connection_verified") == connection_verified_status


def test_slack_event_endpoint(api_client, mock_post_request):
    mock_post_request.status_code = 200
    mock_post_request.json.return_value = {"ok": ""}

    # Send a request to /slack-events
    sample_event_data = {"key": "value"}
    headers = {
        "X-Slack-Signature": "random_invalid_signature",
        "X-Slack-Request-Timestamp": "123457",
    }
    response = api_client.post("/slack-events", headers=headers, json=sample_event_data)
    assert response.status_code == 403


def test_get_apps_per_user_endpoint(api_client):
    # This API requires that the app is created by an admin.
    response = api_client.get("/get-apps/123")
    assert response.status_code == 200
    assert isinstance(response.json()["apps"], list)
