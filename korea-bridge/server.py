from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sources.fdr import get_financial_statements, get_stock_price
from sources.naver import get_news
from firebase_client import get_cached, set_cached

app = FastAPI(title="Korea Bridge", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TTL_FINANCIAL = 86400
TTL_PRICE = 86400
TTL_NEWS = 3600

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/financial-statements/{ticker}")
def financial_statements(ticker: str):
    cache_key = f"fs_{ticker}"
    cached = get_cached("financial_statements", cache_key, TTL_FINANCIAL)
    if cached:
        return cached
    data = get_financial_statements(ticker)
    set_cached("financial_statements", cache_key, data)
    return data

@app.get("/stock-price/{ticker}")
def stock_price(ticker: str, period: str = "1y"):
    cache_key = f"price_{ticker}_{period}"
    cached = get_cached("stock_prices", cache_key, TTL_PRICE)
    if cached:
        return cached
    data = get_stock_price(ticker, period)
    set_cached("stock_prices", cache_key, data)
    return data

@app.get("/news/{ticker}")
def news(ticker: str, limit: int = 10):
    cache_key = f"news_{ticker}"
    cached = get_cached("news", cache_key, TTL_NEWS)
    if cached:
        return cached
    data = get_news(ticker, limit=limit)
    set_cached("news", cache_key, data)
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
