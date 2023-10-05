import hashlib
import hmac
import json

import pytest
from fastapi import HTTPException, status

from app.config.slack_config import settings
from app.utils.dependencies import verify_event, verify_token


def test_verify_token_with_valid_token():
    token = "valid_token"
    result = verify_token(token)
    assert result == token


def test_verify_token_with_missing_token():
    with pytest.raises(HTTPException) as exc_info:
        verify_token(None)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Authentication token is missing"


def test_verify_valid_slack_event_signature():
    # Simulate a valid Slack event signature
    slack_timestamp = 1234567890
    request_body = {"key": "value"}
    event_data_json = json.dumps(request_body, separators=(",", ":")).encode("utf-8")
    expected_signature = (
        "v0="
        + hmac.new(
            settings.SIGNING_SECRET.encode("utf-8"),
            (f"v0:{slack_timestamp}:".encode("utf-8") + event_data_json),
            hashlib.sha256,
        ).hexdigest()
    )

    assert verify_event(expected_signature, slack_timestamp, request_body) == True


def test_verify_invalid_slack_event_signature():
    # Simulate an invalid Slack event signature
    slack_timestamp = 1234567890
    request_body = {"key": "value"}
    invalid_signature = "invalid_signature"

    # Verify the invalid signature
    assert verify_event(invalid_signature, slack_timestamp, request_body) == False
