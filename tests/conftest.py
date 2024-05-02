import pytest
from fastapi.testclient import TestClient

from site_ong.main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
