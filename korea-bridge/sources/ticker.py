import FinanceDataReader as fdr

_name_to_code: dict[str, str] | None = None

def _load_krx_listing() -> dict[str, str]:
    global _name_to_code
    if _name_to_code is None:
        df = fdr.StockListing("KRX")
        _name_to_code = dict(zip(df["Name"], df["Code"]))
    return _name_to_code

def resolve_ticker(name_or_code: str) -> str:
    """한글 종목명 또는 6자리 코드를 6자리 코드로 변환."""
    if name_or_code.isdigit() and len(name_or_code) == 6:
        return name_or_code
    mapping = _load_krx_listing()
    return mapping.get(name_or_code, name_or_code)
