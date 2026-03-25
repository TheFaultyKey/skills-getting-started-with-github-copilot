import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities before each test for isolation
    for name, data in activities.items():
        if name == "Chess Club":
            data["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
        elif name == "Programming Class":
            data["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]
        elif name == "Gym Class":
            data["participants"] = ["john@mergington.edu", "olivia@mergington.edu"]
        else:
            data["participants"] = []

# GET /activities
def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

# POST /activities/{activity_name}/signup (success)
def test_signup_success():
    resp = client.post("/activities/Chess Club/signup?email=tester@mergington.edu")
    assert resp.status_code == 200
    assert "Signed up tester@mergington.edu" in resp.json()["message"]
    # Confirm participant added
    assert "tester@mergington.edu" in activities["Chess Club"]["participants"]

# POST /activities/{activity_name}/signup (duplicate)
def test_signup_duplicate():
    email = "daniel@mergington.edu"
    resp = client.post(f"/activities/Chess Club/signup?email={email}")
    assert resp.status_code == 400
    assert "Student already signed up for this activity" in resp.json()["detail"]

# POST /activities/{activity_name}/signup (activity full)
def test_signup_full():
    # Fill up Chess Club (max 12)
    for i in range(10):
        client.post(f"/activities/Chess Club/signup?email=extra{i}@mergington.edu")
    resp = client.post("/activities/Chess Club/signup?email=last@mergington.edu")
    assert resp.status_code == 400
    assert "Activity is full" in resp.json()["detail"]

# POST /activities/{activity_name}/signup (invalid activity)
def test_signup_invalid_activity():
    resp = client.post("/activities/Nonexistent/signup?email=ghost@mergington.edu")
    assert resp.status_code == 404
    assert "Activity not found" in resp.json()["detail"]

# DELETE /activities/{activity_name}/signup (success)
def test_unregister_success():
    resp = client.delete("/activities/Chess Club/signup?email=daniel@mergington.edu")
    assert resp.status_code == 200
    assert "Unregistered daniel@mergington.edu" in resp.json()["message"]
    assert "daniel@mergington.edu" not in activities["Chess Club"]["participants"]

# DELETE /activities/{activity_name}/signup (not registered)
def test_unregister_not_registered():
    resp = client.delete("/activities/Chess Club/signup?email=ghost@mergington.edu")
    assert resp.status_code == 404
    assert "Participant not found" in resp.json()["detail"]

# DELETE /activities/{activity_name}/signup (invalid activity)
def test_unregister_invalid_activity():
    resp = client.delete("/activities/Nonexistent/signup?email=ghost@mergington.edu")
    assert resp.status_code == 404
    assert "Activity not found" in resp.json()["detail"]

# DELETE /activities/{activity_name}/signup (double unregister)
def test_double_unregister():
    email = "daniel@mergington.edu"
    # First remove
    resp1 = client.delete(f"/activities/Chess Club/signup?email={email}")
    assert resp1.status_code == 200
    # Second remove
    resp2 = client.delete(f"/activities/Chess Club/signup?email={email}")
    assert resp2.status_code == 404
    assert "Participant not found" in resp2.json()["detail"]
