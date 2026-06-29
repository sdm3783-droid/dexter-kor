import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sources.ticker import resolve_ticker

def test_resolve_code_unchanged():
    assert resolve_ticker("005930") == "005930"

def test_resolve_korean_name():
    result = resolve_ticker("삼성전자")
    assert result == "005930"

def test_resolve_unknown_returns_input():
    result = resolve_ticker("UNKNOWN_XYZ")
    assert result == "UNKNOWN_XYZ"
