import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sources.naver import get_news

def test_get_news_samsung():
    result = get_news("005930", limit=5)
    assert result["ticker"] == "005930"
    assert len(result["news"]) > 0
    assert "title" in result["news"][0]
    assert "date" in result["news"][0]
    assert "url" in result["news"][0]
