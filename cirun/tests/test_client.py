import pytest

from cirun import Cirun


def test_raise_error_when_key_not_set():
    with pytest.raises(KeyError):
        Cirun()


def test_not_raise_error_when_token_set():
    Cirun(token="cirun-token-foo-bar")
