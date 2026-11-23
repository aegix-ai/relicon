from fastapi.testclient import TestClient


def test_api_sim_and_learning_roundtrip():
    from relicon.api import app
    c = TestClient(app)
    assert c.get("/api/health").json()["ok"]
    r = c.post("/api/sim/run", json={"generations": 2, "batch": 4}).json()
    assert r["is_simulated"] and len(r["log"]) == 2
    camp = c.get("/api/campaigns").json()
    assert camp[0]["is_simulated"] and camp[0]["ads"] == 8
    lv = c.get("/api/learning/coffee_nightshift").json()
    assert lv["active"]["version"] == "p0002" and len(lv["versions"]) == 2
    assert c.post("/api/learning/coffee_nightshift/rollback", json={"version": "p0001"}).status_code == 200
    assert c.get("/api/learning/coffee_nightshift").json()["active"]["version"] == "p0001"
    assert len(c.get("/api/sim/scenarios").json()) == 12
