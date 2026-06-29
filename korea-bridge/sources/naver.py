import requests
from bs4 import BeautifulSoup
from .ticker import resolve_ticker

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://finance.naver.com",
}

def get_news(name_or_code: str, limit: int = 10) -> dict:
    """네이버금융 종목 뉴스 스크래핑 (개인 학습 목적)."""
    ticker = resolve_ticker(name_or_code)
    url = f"https://finance.naver.com/item/news_news.naver?code={ticker}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = "euc-kr"
        soup = BeautifulSoup(resp.text, "html.parser")
        # 뉴스 링크 직접 추출
        links = soup.select("a[href*='news_read']")
        news_list = []
        seen = set()
        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)
            if not title or href in seen:
                continue
            seen.add(href)
            # 날짜는 부모 행에서 찾기
            parent_row = link.find_parent("tr")
            date_tag = parent_row.select_one("td.date") if parent_row else None
            news_list.append({
                "title": title,
                "url": "https://finance.naver.com" + href,
                "date": date_tag.get_text(strip=True) if date_tag else "",
                "summary": "",
            })
            if len(news_list) >= limit:
                break
        return {"ticker": ticker, "news": news_list}
    except Exception as e:
        return {"ticker": ticker, "news": [], "error": str(e)}
