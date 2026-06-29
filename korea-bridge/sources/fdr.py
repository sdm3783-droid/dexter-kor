import FinanceDataReader as fdr
import datetime
from .ticker import resolve_ticker

def get_financial_statements(name_or_code: str) -> dict:
    ticker = resolve_ticker(name_or_code)
    try:
        df = fdr.DataReader(f"KRX/SRT02010100/{ticker}")
        records = df.reset_index().to_dict(orient="records") if df is not None and not df.empty else []
    except Exception:
        records = []
    return {"ticker": ticker, "statements": records}

def get_stock_price(name_or_code: str, period: str = "1y") -> dict:
    ticker = resolve_ticker(name_or_code)
    end = datetime.date.today()
    years = int(period.replace("y", "")) if period.endswith("y") else 1
    start = end.replace(year=end.year - years)
    try:
        df = fdr.DataReader(ticker, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
        if df is None or df.empty:
            return {"ticker": ticker, "prices": []}
        prices = [
            {"date": str(idx.date()), "close": int(row["Close"]), "volume": int(row["Volume"])}
            for idx, row in df.iterrows()
        ]
    except Exception:
        prices = []
    return {"ticker": ticker, "prices": prices}
