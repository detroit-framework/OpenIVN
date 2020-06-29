"""Tests API key authentication."""
import requests


def test_api_key_success():
    """Tests using a valid API key."""
    url = "http://localhost:1609/api/v1/hello_world/"
    headers = {
        'x-api-key': 'insert an api key'
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200


def test_api_key_unauthorized():
    """Tests using an invalid API key."""
    url = "http://localhost:1609/api/v1/hello_world/"
    response = requests.get(url)
    assert response.status_code == 401


if __name__ == '__main__':
    test_api_key_success()
    test_api_key_unauthorized()
