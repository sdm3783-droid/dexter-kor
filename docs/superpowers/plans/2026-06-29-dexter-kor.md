# Dexter KOR Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** virattt/dexter를 클론해서 미국 주식으로 검증한 뒤, Python FastAPI Korea Bridge + Firebase 캐시 레이어를 추가해 한국 주식 분석이 가능한 에이전트를 완성한다.

**Architecture:** Dexter(TypeScript/Bun) 에이전트가 질문을 분해하고, Korea Bridge(Python FastAPI :8000)의 엔드포인트를 도구로 호출해 KRX 금융 데이터를 가져온다. 조회된 데이터는 Firebase Firestore(dexter-kor 프로젝트)에 TTL 캐시로 저장된다.

**Tech Stack:** TypeScript, Bun 1.3.x, OpenAI GPT-4o, Python 3.14, FastAPI, FinanceDataReader, pykrx, requests+BeautifulSoup, Firebase Admin SDK

## Global Constraints

- 작업 디렉토리: `D:\Claude_Code\프로그램 구축자료실\DEXTER(KOR)\`
- 포트: Korea Bridge는 반드시 `8000` 사용 (3000/8080 금지)
- Firebase: `dexter-kor` 전용 프로젝트 사용 (기존 ske-0004 등과 분리)
- 네이버금융 스크래핑: 개인 학습/연구 목적 전용
- 실제 투자 매매 사용 금지

---

## 파일 맵

```
DEXTER(KOR)/
├── dexter/                          ← Task 1에서 클론
│   └── src/
│       └── tools/
│           └── korean_financial.ts  ← Task 5에서 생성
├── korea-bridge/
│   ├── requirements.txt             ← Task 2에서 생성
│   ├── server.py                    ← Task 3에서 생성
│   ├── firebase_client.py           ← Task 3에서 생성
│   └── sources/
│       ├── __init__.py              ← Task 2에서 생성
│       ├── ticker.py                ← Task 2에서 생성
│       ├── fdr.py                   ← Task 3에서 생성
│       ├── pykrx_source.py          ← Task 3에서 생성
│       └── naver.py                 ← Task 4에서 생성
├── .env                             ← Task 1에서 생성
└── README.md                        ← Task 6에서 생성
```

---

### Task 1: Dexter 클론 + 환경 세팅 + 실행 검증

**Files:**
- Clone: `dexter/` (from https://github.com/virattt/dexter)
- Create: `.env`

**Interfaces:**
- Produces: 작동하는 Dexter 인스턴스, `.env` 파일 구조

- [ ] **Step 1: 작업 디렉토리로 이동**

```bash
cd "D:\Claude_Code\프로그램 구축자료실\DEXTER(KOR)"
```

- [ ] **Step 2: Dexter 클론**

```bash
git clone https://github.com/virattt/dexter.git dexter
```

Expected: `dexter/` 폴더 생성됨

- [ ] **Step 3: Dexter 구조 파악**

```bash
ls dexter/src/
cat dexter/package.json
```

Expected: `src/` 하위에 `tools/`, `agent/` 등 폴더 확인

- [ ] **Step 4: .env 생성**

`DEXTER(KOR)/.env` 내용:
```env
# OpenAI
OPENAI_API_KEY=sk-...여기에_실제키_입력...

# Korea Bridge
KOREA_BRIDGE_URL=http://localhost:8000

# Firebase (Task 3에서 채울 것)
FIREBASE_PROJECT_ID=
FIREBASE_PRIVATE_KEY=
FIREBASE_CLIENT_EMAIL=
```

- [ ] **Step 5: Dexter 의존성 설치**

```bash
cd dexter
bun install
```

Expected: `node_modules/` 생성, 에러 없음

- [ ] **Step 6: Dexter .env 심볼릭 링크 또는 복사**

Dexter는 자체 `.env`를 읽으므로 루트 `.env`를 `dexter/` 안에도 복사:
```bash
cp ../.env .env
```

- [ ] **Step 7: Dexter 실행 확인**

```bash
bun run dev
```

Expected: 에이전트 프롬프트 또는 인터페이스 표시됨. 에러 없이 시작됨.

- [ ] **Step 8: 미국 주식 검증 쿼리 실행**

Dexter 인터페이스에서 입력:
```
What is Apple's revenue trend over the last 3 years?
```

Expected: 에이전트가 Financial Datasets API를 호출해 AAPL 재무 데이터 조회 후 분석 결과 출력

- [ ] **Step 9: 커밋**

```bash
cd ..
git add .env
git commit -m "feat: clone dexter and verify US stock analysis"
```

---

### Task 2: Korea Bridge 기반 구조 — ticker 변환 + 패키지

**Files:**
- Create: `korea-bridge/requirements.txt`
- Create: `korea-bridge/sources/__init__.py`
- Create: `korea-bridge/sources/ticker.py`

**Interfaces:**
- Produces:
  - `resolve_ticker(name_or_code: str) -> str` — "삼성전자" 또는 "005930" → "005930" 반환

- [ ] **Step 1: korea-bridge 폴더 생성**

```bash
mkdir -p korea-bridge/sources
```

- [ ] **Step 2: requirements.txt 작성**

`korea-bridge/requirements.txt`:
```
fastapi==0.115.0
uvicorn==0.30.6
FinanceDataReader==0.9.50
pykrx==1.0.47
requests==2.32.3
beautifulsoup4==4.12.3
firebase-admin==6.5.0
python-dotenv==1.0.1
```

- [ ] **Step 3: 테스트 먼저 작성**

`korea-bridge/tests/test_ticker.py`:
```python
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
```

- [ ] **Step 4: 테스트 실패 확인**

```bash
cd korea-bridge
pip install -r requirements.txt
python -m pytest tests/test_ticker.py -v
```

Expected: FAIL (ImportError — ticker.py 없음)

- [ ] **Step 5: ticker.py 구현**

`korea-bridge/sources/ticker.py`:
```python
import FinanceDataReader as fdr

_name_to_code: dict[str, str] | None = None

def _load_krx_listing() -> dict[str, str]:
    global _name_to_code
    if _name_to_code is None:
        df = fdr.StockListing('KRX')
        _name_to_code = dict(zip(df['Name'], df['Code']))
    return _name_to_code

def resolve_ticker(name_or_code: str) -> str:
    """한글 종목명 또는 6자리 코드를 6자리 코드로 변환."""
    if name_or_code.isdigit() and len(name_or_code) == 6:
        return name_or_code
    mapping = _load_krx_listing()
    return mapping.get(name_or_code, name_or_code)
```

- [ ] **Step 6: __init__.py 생성**

`korea-bridge/sources/__init__.py`:
```python
from .ticker import resolve_ticker
```

- [ ] **Step 7: 테스트 통과 확인**

```bash
python -m pytest tests/test_ticker.py -v
```

Expected: 3개 PASS

- [ ] **Step 8: 커밋**

```bash
cd ..
git add korea-bridge/
git commit -m "feat: add ticker name-to-code resolver"
```

---

### Task 3: Korea Bridge — 재무제표 + 주가 엔드포인트 + Firebase 캐시

**Files:**
- Create: `korea-bridge/firebase_client.py`
- Create: `korea-bridge/sources/fdr.py`
- Create: `korea-bridge/sources/pykrx_source.py`
- Create: `korea-bridge/server.py`

**Interfaces:**
- Consumes: `resolve_ticker()` from Task 2
- Produces:
  - `GET /financial-statements/{ticker}` → `{ "income": [...], "balance": [...], "cashflow": [...] }`
  - `GET /stock-price/{ticker}?period=1y` → `{ "ticker": str, "prices": [{"date": str, "close": int, "volume": int}] }`

- [ ] **Step 1: Firebase 서비스 계정 키 준비**

[Firebase Console](https://console.firebase.google.com) → dexter-kor 프로젝트 → 프로젝트 설정 → 서비스 계정 → 새 비공개 키 생성 → JSON 다운로드

`DEXTER(KOR)/.env`에 추가:
```env
FIREBASE_PROJECT_ID=dexter-kor
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@dexter-kor.iam.gserviceaccount.com
```

- [ ] **Step 2: firebase_client.py 작성**

`korea-bridge/firebase_client.py`:
```python
import os, time
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

_db = None

def get_db():
    global _db
    if _db is None:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.environ["FIREBASE_PROJECT_ID"],
            "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
            "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
            "token_uri": "https://oauth2.googleapis.com/token",
        })
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
    return _db

def get_cached(collection: str, doc_id: str, ttl_seconds: int) -> dict | None:
    db = get_db()
    doc = db.collection(collection).document(doc_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    if time.time() - data.get("cached_at", 0) > ttl_seconds:
        return None
    return data.get("payload")

def set_cached(collection: str, doc_id: str, payload: dict):
    db = get_db()
    db.collection(collection).document(doc_id).set({
        "payload": payload,
        "cached_at": time.time(),
    })
```

- [ ] **Step 3: fdr.py 작성**

`korea-bridge/sources/fdr.py`:
```python
import FinanceDataReader as fdr
from .ticker import resolve_ticker

def get_financial_statements(name_or_code: str) -> dict:
    """FinanceDataReader로 재무제표 조회."""
    ticker = resolve_ticker(name_or_code)
    try:
        df_fs = fdr.DataReader(f'KRX/SRT02010100/{ticker}')
        records = df_fs.reset_index().to_dict(orient='records') if df_fs is not None and not df_fs.empty else []
    except Exception:
        records = []
    return {"ticker": ticker, "statements": records}

def get_stock_price(name_or_code: str, period: str = "1y") -> dict:
    """pykrx 없이 FDR로 주가 조회."""
    import datetime
    ticker = resolve_ticker(name_or_code)
    end = datetime.date.today()
    years = int(period.replace("y", "")) if period.endswith("y") else 1
    start = end.replace(year=end.year - years)
    df = fdr.DataReader(ticker, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    if df is None or df.empty:
        return {"ticker": ticker, "prices": []}
    prices = [
        {"date": str(idx.date()), "close": int(row["Close"]), "volume": int(row["Volume"])}
        for idx, row in df.iterrows()
    ]
    return {"ticker": ticker, "prices": prices}
```

- [ ] **Step 4: pykrx_source.py 작성**

`korea-bridge/sources/pykrx_source.py`:
```python
from pykrx import stock
from .ticker import resolve_ticker
import datetime

def get_market_cap(name_or_code: str) -> dict:
    """pykrx로 시가총액 및 기본 지표 조회."""
    ticker = resolve_ticker(name_or_code)
    today = datetime.date.today().strftime("%Y%m%d")
    try:
        df = stock.get_market_cap_by_ticker(today)
        if ticker in df.index:
            row = df.loc[ticker]
            return {
                "ticker": ticker,
                "market_cap": int(row.get("시가총액", 0)),
                "shares": int(row.get("상장주식수", 0)),
            }
    except Exception:
        pass
    return {"ticker": ticker, "market_cap": None, "shares": None}
```

- [ ] **Step 5: 테스트 작성**

`korea-bridge/tests/test_data_sources.py`:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sources.fdr import get_stock_price

def test_stock_price_samsung():
    result = get_stock_price("005930", period="1y")
    assert result["ticker"] == "005930"
    assert len(result["prices"]) > 0
    assert "close" in result["prices"][0]
    assert "date" in result["prices"][0]

def test_stock_price_by_name():
    result = get_stock_price("삼성전자", period="1y")
    assert result["ticker"] == "005930"
```

- [ ] **Step 6: 테스트 실행**

```bash
cd korea-bridge
python -m pytest tests/test_data_sources.py -v
```

Expected: 2개 PASS (실제 API 호출)

- [ ] **Step 7: server.py 작성**

`korea-bridge/server.py`:
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sources.fdr import get_financial_statements, get_stock_price
from sources.pykrx_source import get_market_cap
from firebase_client import get_cached, set_cached
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

app = FastAPI(title="Korea Bridge", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TTL_FINANCIAL = 86400      # 1일
TTL_PRICE = 86400          # 1일
TTL_NEWS = 3600            # 1시간

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

@app.get("/market-cap/{ticker}")
def market_cap(ticker: str):
    data = get_market_cap(ticker)
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
```

- [ ] **Step 8: 서버 실행 테스트**

```bash
python server.py
```

다른 터미널에서:
```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

```bash
curl "http://localhost:8000/stock-price/005930?period=1y"
```

Expected: JSON with `ticker` and `prices` array

- [ ] **Step 9: 커밋**

```bash
cd ..
git add korea-bridge/
git commit -m "feat: add Korea Bridge with financial statements and stock price endpoints"
```

---

### Task 4: Korea Bridge — 뉴스/공시 엔드포인트

**Files:**
- Create: `korea-bridge/sources/naver.py`

**Interfaces:**
- Consumes: `resolve_ticker()` from Task 2
- Produces:
  - `GET /news/{ticker}` → `{ "ticker": str, "news": [{"title": str, "date": str, "url": str, "summary": str}] }`

- [ ] **Step 1: 테스트 작성**

`korea-bridge/tests/test_naver.py`:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sources.naver import get_news

def test_get_news_samsung():
    result = get_news("005930", limit=5)
    assert result["ticker"] == "005930"
    assert len(result["news"]) > 0
    assert "title" in result["news"][0]
    assert "date" in result["news"][0]
    assert "url" in result["news"][0]
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
cd korea-bridge
python -m pytest tests/test_naver.py -v
```

Expected: FAIL (ImportError)

- [ ] **Step 3: naver.py 구현**

`korea-bridge/sources/naver.py`:
```python
import requests
from bs4 import BeautifulSoup
from .ticker import resolve_ticker

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}

def get_news(name_or_code: str, limit: int = 10) -> dict:
    """네이버금융에서 종목 관련 뉴스 스크래핑 (개인 학습 목적)."""
    ticker = resolve_ticker(name_or_code)
    url = f"https://finance.naver.com/item/news_news.naver?code={ticker}&page=1"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = "euc-kr"
        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.select("table.type5 tr")
        news_list = []
        for row in rows:
            title_tag = row.select_one("td.title a")
            date_tag = row.select_one("td.date")
            if not title_tag or not date_tag:
                continue
            news_list.append({
                "title": title_tag.get_text(strip=True),
                "url": "https://finance.naver.com" + title_tag["href"],
                "date": date_tag.get_text(strip=True),
                "summary": "",
            })
            if len(news_list) >= limit:
                break
        return {"ticker": ticker, "news": news_list}
    except Exception as e:
        return {"ticker": ticker, "news": [], "error": str(e)}
```

- [ ] **Step 4: server.py에 뉴스 엔드포인트 추가**

`korea-bridge/server.py`에 import 추가:
```python
from sources.naver import get_news
```

엔드포인트 추가:
```python
@app.get("/news/{ticker}")
def news(ticker: str, limit: int = 10):
    cache_key = f"news_{ticker}"
    cached = get_cached("news", cache_key, TTL_NEWS)
    if cached:
        return cached
    data = get_news(ticker, limit=limit)
    set_cached("news", cache_key, data)
    return data
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
python -m pytest tests/test_naver.py -v
```

Expected: PASS

- [ ] **Step 6: 엔드포인트 실제 확인**

```bash
curl "http://localhost:8000/news/005930?limit=3"
```

Expected: JSON with `ticker` and `news` array (3건 이하)

- [ ] **Step 7: 커밋**

```bash
cd ..
git add korea-bridge/sources/naver.py korea-bridge/server.py korea-bridge/tests/test_naver.py
git commit -m "feat: add naver finance news scraping endpoint"
```

---

### Task 5: Dexter에 한국 금융 도구 연결

**Files:**
- Create: `dexter/src/tools/korean_financial.ts`
- Modify: Dexter tool registry (경로는 Task 1 실행 후 `ls dexter/src/tools/` 로 확인)

**Interfaces:**
- Consumes: Korea Bridge running on `http://localhost:8000`
- Produces: `koreanFinancialStatements`, `koreanStockPrice`, `koreanNews` tool definitions

> **주의:** 이 Task 실행 전 `ls dexter/src/tools/` 및 `cat dexter/src/tools/index.ts` (또는 해당 파일)을 먼저 실행해서 기존 tool 등록 패턴을 파악할 것.

- [ ] **Step 1: Dexter tool 등록 방식 파악**

```bash
ls dexter/src/tools/
cat dexter/src/tools/index.ts
```

Expected: 기존 Financial Datasets API 도구 정의 패턴 확인

- [ ] **Step 2: korean_financial.ts 작성**

`dexter/src/tools/korean_financial.ts`:
```typescript
const KOREA_BRIDGE = process.env.KOREA_BRIDGE_URL ?? "http://localhost:8000";

async function fetchBridge(path: string): Promise<unknown> {
  const res = await fetch(`${KOREA_BRIDGE}${path}`);
  if (!res.ok) throw new Error(`Korea Bridge error: ${res.status} ${path}`);
  return res.json();
}

export const koreanFinancialStatements = {
  name: "korean_financial_statements",
  description:
    "한국 상장 종목의 재무제표(손익계산서, 대차대조표, 현금흐름표)를 조회합니다. 종목명(삼성전자) 또는 6자리 코드(005930) 모두 허용.",
  parameters: {
    type: "object" as const,
    properties: {
      ticker: {
        type: "string",
        description: "종목명(예: 삼성전자) 또는 6자리 종목코드(예: 005930)",
      },
    },
    required: ["ticker"],
  },
  execute: async ({ ticker }: { ticker: string }) => {
    return fetchBridge(`/financial-statements/${encodeURIComponent(ticker)}`);
  },
};

export const koreanStockPrice = {
  name: "korean_stock_price",
  description:
    "한국 상장 종목의 주가 히스토리를 조회합니다. period는 '1y'(1년), '3y'(3년) 형식.",
  parameters: {
    type: "object" as const,
    properties: {
      ticker: { type: "string", description: "종목명 또는 6자리 종목코드" },
      period: { type: "string", description: "조회 기간 (예: 1y, 3y)", default: "1y" },
    },
    required: ["ticker"],
  },
  execute: async ({ ticker, period = "1y" }: { ticker: string; period?: string }) => {
    return fetchBridge(`/stock-price/${encodeURIComponent(ticker)}?period=${period}`);
  },
};

export const koreanNews = {
  name: "korean_news",
  description: "네이버금융에서 해당 종목의 최신 뉴스/공시를 가져옵니다.",
  parameters: {
    type: "object" as const,
    properties: {
      ticker: { type: "string", description: "종목명 또는 6자리 종목코드" },
      limit: { type: "number", description: "가져올 뉴스 수 (기본 10)", default: 10 },
    },
    required: ["ticker"],
  },
  execute: async ({ ticker, limit = 10 }: { ticker: string; limit?: number }) => {
    return fetchBridge(`/news/${encodeURIComponent(ticker)}?limit=${limit}`);
  },
};
```

- [ ] **Step 3: tool registry에 한국 도구 등록**

Step 1에서 파악한 패턴에 따라 `korean_financial.ts`의 3개 도구를 기존 tool 목록에 추가.

예시 (실제 파일 구조 확인 후 적용):
```typescript
import { koreanFinancialStatements, koreanStockPrice, koreanNews } from "./korean_financial";

// 기존 tools 배열에 추가
export const tools = [
  ...existingTools,
  koreanFinancialStatements,
  koreanStockPrice,
  koreanNews,
];
```

- [ ] **Step 4: TypeScript 컴파일 확인**

```bash
cd dexter
bun run build 2>/dev/null || bun tsc --noEmit
```

Expected: 에러 없음

- [ ] **Step 5: Dexter 재실행 후 한국 주식 쿼리 테스트**

터미널 1 (Korea Bridge 실행 중인지 확인):
```bash
curl http://localhost:8000/health
```

터미널 2:
```bash
cd dexter && bun run dev
```

Dexter에서 입력:
```
삼성전자의 최근 1년 주가 흐름과 최신 뉴스를 분석해줘
```

Expected: Korea Bridge 도구 호출 로그 보임, 분석 결과 출력됨

- [ ] **Step 6: 커밋**

```bash
cd ..
git add dexter/src/tools/korean_financial.ts
git commit -m "feat: add Korean financial data tools to Dexter"
```

---

### Task 6: README 및 실행 가이드 작성

**Files:**
- Create: `README.md`

- [ ] **Step 1: README.md 작성**

`DEXTER(KOR)/README.md`:
```markdown
# Dexter KOR

virattt/dexter 기반 한국 주식 자율 금융 리서치 에이전트.

## 사전 요구사항

- Bun 1.3+
- Python 3.14+
- OpenAI API 키
- Firebase 프로젝트 (dexter-kor)

## 환경 설정

`.env` 파일 작성:
```env
OPENAI_API_KEY=sk-...
KOREA_BRIDGE_URL=http://localhost:8000
FIREBASE_PROJECT_ID=dexter-kor
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@dexter-kor.iam.gserviceaccount.com
```

## 실행

**터미널 1 — Korea Bridge (데이터 서버):**
```bash
cd korea-bridge
pip install -r requirements.txt
python server.py
```

**터미널 2 — Dexter 에이전트:**
```bash
cd dexter
cp ../.env .env
bun install
bun run dev
```

## 사용 예시

```
삼성전자의 최근 3년 실적을 분석해줘
현대차와 기아의 영업이익률을 비교해줘
코스피 반도체 섹터 최근 뉴스 요약해줘
```

## 주의사항

- 개인 학습/연구 목적 전용
- 실제 투자 매매에 사용 금지
- 네이버금융 스크래핑은 이용약관 범위 내 사용
```

- [ ] **Step 2: 커밋 및 푸시**

```bash
git add README.md
git commit -m "docs: add README with setup and usage guide"
git push
```

---

## 테스트 체크리스트

- [ ] `curl http://localhost:8000/health` → `{"status":"ok"}`
- [ ] `curl http://localhost:8000/stock-price/005930` → prices 배열 포함
- [ ] `curl http://localhost:8000/news/005930` → news 배열 포함
- [ ] Dexter에서 "삼성전자 분석해줘" → Korea Bridge 도구 호출 확인
- [ ] Firebase Console에서 `stock_prices`, `news` 컬렉션 데이터 확인
