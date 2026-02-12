from unittest.mock import patch, AsyncMock


class TestShortenEndpoint:


    @patch("app.routes.check_url_accessible", new_callable=AsyncMock, return_value=True)
    def test_shorten_success(self, mock_check, client):
        response = client.post(
            "/api/shorten",
            json={"url": "https://www.google.com"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "short_url" in data
        assert "short_code" in data
        assert data["original_url"] == "https://www.google.com"


    @patch("app.routes.check_url_accessible", new_callable=AsyncMock, return_value=True)
    def test_shorten_custom_code(self, mock_check, client):
        response = client.post(
            "/api/shorten",
            json={"url": "https://www.google.com", "custom_code": "my-link"},
        )
        assert response.status_code == 201
        assert response.json()["short_code"] == "my-link"


    @patch("app.routes.check_url_accessible", new_callable=AsyncMock, return_value=True)
    def test_shorten_duplicate_custom_code(self, mock_check, client):
        client.post(
            "/api/shorten",
            json={"url": "https://google.com", "custom_code": "taken"},
        )
        response = client.post(
            "/api/shorten",
            json={"url": "https://ya.ru", "custom_code": "taken"},
        )
        assert response.status_code == 409


    @patch("app.routes.check_url_accessible", new_callable=AsyncMock, return_value=False)
    def test_shorten_invalid_url(self, mock_check, client):
        response = client.post(
            "/api/shorten",
            json={"url": "not-a-valid-url"},
        )
        assert response.status_code == 400


    @patch("app.routes.check_url_accessible", new_callable=AsyncMock, return_value=False)
    def test_shorten_inaccessible_url(self, mock_check, client):
        response = client.post(
            "/api/shorten",
            json={"url": "https://thisdomaindoesnotexist12345.com"},
        )
        assert response.status_code == 400


    @patch("app.routes.check_url_accessible", new_callable=AsyncMock, return_value=True)
    def test_shorten_idempotent(self, mock_check, client):
        r1 = client.post("/api/shorten", json={"url": "https://google.com"})
        r2 = client.post("/api/shorten", json={"url": "https://google.com"})
        assert r1.json()["short_code"] == r2.json()["short_code"]


class TestRedirectEndpoint:


    @patch("app.routes.check_url_accessible", new_callable=AsyncMock, return_value=True)
    def test_redirect_success(self, mock_check, client):
        resp = client.post(
            "/api/shorten",
            json={"url": "https://www.google.com", "custom_code": "ggl"},
        )
        redirect = client.get("/ggl", follow_redirects=False)
        assert redirect.status_code == 302
        assert redirect.headers["location"] == "https://www.google.com"

    def test_redirect_not_found(self, client):
        response = client.get("/nonexistent", follow_redirects=False)
        assert response.status_code == 404


class TestInfoEndpoint:

    @patch("app.routes.check_url_accessible", new_callable=AsyncMock, return_value=True)
    def test_info_with_clicks(self, mock_check, client):
        client.post(
            "/api/shorten",
            json={"url": "https://google.com", "custom_code": "test"},
        )
        for _ in range(3):
            client.get("/test", follow_redirects=False)

        info = client.get("/api/info/test")
        assert info.status_code == 200
        assert info.json()["clicks"] == 3
