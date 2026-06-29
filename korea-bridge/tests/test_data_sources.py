import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sources.fdr import get_stock_price

def test_stock_price_samsung_code():
    result = get_stock_price("005930", period="1y")
    assert result["ticker"] == "005930"
    assert len(result["prices"]) > 0
    assert "close" in result["prices"][0]
    assert "date" in result["prices"][0]

def test_stock_price_samsung_name():
    result = get_stock_price("삼성전자", period="1y")
    assert result["ticker"] == "005930"
    assert len(result["prices"]) > 0
