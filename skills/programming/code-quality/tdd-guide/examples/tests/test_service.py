import pytest
from service import login

def test_login_ok():
    assert login("u", "p") == "token-placeholder"

def test_login_missing():
    with pytest.raises(ValueError):
        login("", "")
