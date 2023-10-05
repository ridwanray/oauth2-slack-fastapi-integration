from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def api_client():
    client = TestClient(app)
    return client


@pytest.fixture
def mock_get_request(mocker):
    mock = Mock()
    mocker.patch("requests.get", return_value=mock)
    return mock


@pytest.fixture
def mock_post_request(mocker):
    mock = Mock()
    mocker.patch("requests.post", return_value=mock)
    return mock


@pytest.fixture
def mock_async_get():
    with patch("aiohttp.ClientSession.get") as mock_get:
        yield mock_get

@pytest.fixture
def mock_async_post():
    with patch("aiohttp.ClientSession.post") as mock_post:
        yield mock_post