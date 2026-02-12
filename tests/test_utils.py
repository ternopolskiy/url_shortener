import pytest
from app.utils import generate_short_code, SAFE_ALPHABET


def test_code_length():
    code = generate_short_code(8)
    assert len(code) == 8


def test_code_default_length():
    code = generate_short_code()
    assert len(code) == 6


def test_code_uses_safe_alphabet():
    for _ in range(100):
        code = generate_short_code()
        assert all(c in SAFE_ALPHABET for c in code)


def test_code_uniqueness():
    codes = {generate_short_code() for _ in range(1000)}
    assert len(codes) == 1000
