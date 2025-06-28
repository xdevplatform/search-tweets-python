"""Shared pytest fixtures and configuration for all tests."""
import os
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
import pytest
import yaml


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup after test
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Provide a mock configuration dictionary for testing."""
    return {
        "search_tweets_api": {
            "endpoint": "https://api.twitter.com/1.1/tweets/search/30day/test.json",
            "consumer_key": "test_consumer_key",
            "consumer_secret": "test_consumer_secret",
            "bearer_token": "test_bearer_token"
        }
    }


@pytest.fixture
def mock_yaml_config(temp_dir: Path, mock_config: Dict[str, Any]) -> Path:
    """Create a temporary YAML configuration file."""
    config_path = temp_dir / "test_config.yaml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(mock_config, f)
    return config_path


@pytest.fixture
def mock_credentials() -> Dict[str, str]:
    """Provide mock API credentials for testing."""
    return {
        "consumer_key": "test_consumer_key",
        "consumer_secret": "test_consumer_secret",
        "access_token": "test_access_token",
        "access_token_secret": "test_access_token_secret",
        "bearer_token": "test_bearer_token"
    }


@pytest.fixture
def mock_tweet_response() -> Dict[str, Any]:
    """Provide a mock tweet API response for testing."""
    return {
        "results": [
            {
                "id": "1234567890",
                "text": "This is a test tweet",
                "created_at": "2023-01-01T00:00:00Z",
                "user": {
                    "id": "987654321",
                    "screen_name": "test_user"
                }
            }
        ],
        "next": "next_token_value"
    }


@pytest.fixture
def mock_search_params() -> Dict[str, Any]:
    """Provide mock search parameters for testing."""
    return {
        "query": "python",
        "fromDate": "202301010000",
        "toDate": "202301020000",
        "maxResults": 100
    }


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    # Clear any existing Twitter API environment variables
    env_vars = [
        "TWITTER_CONSUMER_KEY",
        "TWITTER_CONSUMER_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET",
        "TWITTER_BEARER_TOKEN"
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)
    
    # Set test environment flag
    monkeypatch.setenv("TESTING", "true")


@pytest.fixture
def capture_logs(caplog):
    """Fixture to capture log messages during tests."""
    with caplog.at_level("DEBUG"):
        yield caplog