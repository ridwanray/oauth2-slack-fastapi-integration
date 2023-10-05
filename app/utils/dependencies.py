import hashlib
import hmac
import json

from fastapi import Header, HTTPException, status

from app.config.slack_config import settings


def verify_token(auth_token: str = Header(None)):
    """Verify that authentication token is included as header"""
    if auth_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_token


def verify_event(slack_signature: str, slack_time: int, body: dict) -> bool:
    """Verify that event is from Slack"""
    slack_signing_secret = settings.SIGNING_SECRET.encode("utf-8")
    event_data_json = json.dumps(body, separators=(",", ":")).encode("utf-8")
    expected_signature = (
        "v0="
        + hmac.new(
            slack_signing_secret,
            (f"v0:{slack_time}:".encode("utf-8") + event_data_json),
            hashlib.sha256,
        ).hexdigest()
    )
    return hmac.compare_digest(expected_signature, slack_signature)
