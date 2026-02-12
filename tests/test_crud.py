from app.crud import create_short_url, get_url_by_code, increment_clicks


def test_create_and_get(db_session):
    url = create_short_url(db_session, "https://example.com", "abc")
    found = get_url_by_code(db_session, "abc")
    assert found is not None
    assert found.original_url == "https://example.com"


def test_clicks_increment(db_session):
    url = create_short_url(db_session, "https://example.com", "xyz")
    assert url.clicks == 0
    increment_clicks(db_session, url)
    increment_clicks(db_session, url)
    assert url.clicks == 2


def test_get_nonexistent(db_session):
    assert get_url_by_code(db_session, "nope") is None
