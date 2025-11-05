import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine


@pytest.fixture(autouse=True, scope="module")
def setup_db():
    # Ensure fresh tables for tests
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_openapi_docs_available():
    client = TestClient(app)
    r = client.get("/docs")
    assert r.status_code == 200
    r = client.get("/redoc")
    assert r.status_code == 200


def test_crud_flow():
    client = TestClient(app)

    # Initially empty
    r = client.get("/terms")
    assert r.status_code == 200
    assert r.json() == []

    # Create term
    payload = {"term": "FastAPI", "description": "A modern, fast web framework."}
    r = client.post("/terms", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["term"] == "FastAPI"

    # Conflict on duplicate
    r = client.post("/terms", json=payload)
    assert r.status_code == 409

    # Get by name
    r = client.get("/terms/FastAPI")
    assert r.status_code == 200
    assert r.json()["description"] == "A modern, fast web framework."

    # Update
    r = client.put("/terms/FastAPI", json={"description": "Fast web framework for building APIs."})
    assert r.status_code == 200
    assert r.json()["description"] == "Fast web framework for building APIs."

    # List has 1
    r = client.get("/terms")
    assert r.status_code == 200
    assert len(r.json()) == 1

    # Delete
    r = client.delete("/terms/FastAPI")
    assert r.status_code == 204

    # Not found after delete
    r = client.get("/terms/FastAPI")
    assert r.status_code == 404

