import json
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestIndex:
    def test_index_returns_ok(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_index_has_version(self, client):
        data = client.get("/").get_json()
        assert "version" in data
        assert data["version"] == "1.0.0"


class TestHealth:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_body(self, client):
        data = client.get("/health").get_json()
        assert data["status"] == "healthy"


class TestHello:
    def test_hello_default(self, client):
        data = client.get("/hello").get_json()
        assert data["message"] == "Hello, World!"

    def test_hello_with_name(self, client):
        data = client.get("/hello?name=CI%2FCD").get_json()
        assert data["message"] == "Hello, CI/CD!"


class TestAdd:
    def test_add_get(self, client):
        data = client.get("/api/add?a=3&b=5").get_json()
        assert data["result"] == 8

    def test_add_post_json(self, client):
        data = client.post(
            "/api/add",
            data=json.dumps({"a": 10, "b": 7}),
            content_type="application/json"
        ).get_json()
        assert data["result"] == 17

    def test_add_negative(self, client):
        data = client.get("/api/add?a=-5&b=3").get_json()
        assert data["result"] == -2

    def test_add_invalid(self, client):
        resp = client.get("/api/add?a=abc&b=5")
        assert resp.status_code == 400


class TestMultiply:
    def test_multiply_get(self, client):
        data = client.get("/api/multiply?a=4&b=6").get_json()
        assert data["result"] == 24

    def test_multiply_post_json(self, client):
        data = client.post(
            "/api/multiply",
            data=json.dumps({"a": 7, "b": 8}),
            content_type="application/json"
        ).get_json()
        assert data["result"] == 56

    def test_multiply_by_zero(self, client):
        data = client.get("/api/multiply?a=100&b=0").get_json()
        assert data["result"] == 0

    def test_multiply_missing_params(self, client):
        resp = client.get("/api/multiply")
        assert resp.status_code == 400


class TestFloatArithmetic:
    def test_add_floats(self, client):
        data = client.get("/api/add?a=1.5&b=2.5").get_json()
        assert abs(data["result"] - 4.0) < 1e-9

    def test_multiply_floats(self, client):
        data = client.get("/api/multiply?a=2.5&b=4").get_json()
        assert abs(data["result"] - 10.0) < 1e-