import os
import sys
import json
import tempfile

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Ensure at least one known activity exists
    assert "Chess Club" in data


def test_signup_and_remove_participant():
    activity = "Chess Club"
    email = "test_user@example.com"

    # Ensure the email is not already registered
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    assert email not in activities[activity]["participants"]

    # Sign up the participant
    signup_resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup_resp.status_code == 200
    signup_json = signup_resp.json()
    assert "Signed up" in signup_json.get("message", "")

    # Confirm participant appears in activity
    resp_after = client.get("/activities")
    activities_after = resp_after.json()
    assert email in activities_after[activity]["participants"]

    # Attempt duplicate signup should fail (400)
    dup_resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert dup_resp.status_code == 400

    # Remove the participant
    del_resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert del_resp.status_code == 200
    del_json = del_resp.json()
    assert "Unregistered" in del_json.get("message", "")

    # Confirm removal
    final_resp = client.get("/activities")
    final_activities = final_resp.json()
    assert email not in final_activities[activity]["participants"]
