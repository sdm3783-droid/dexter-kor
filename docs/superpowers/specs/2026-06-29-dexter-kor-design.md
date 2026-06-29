# Dexter KOR — 설계 스펙

**날짜:** 2026-06-29  
**작업 디렉토리:** `D:\Claude_Code\프로그램 구축자료실\DEXTER(KOR)`

---

## 개요

[virattt/dexter](https://github.com/virattt/dexter) 원본을 기반으로, 미국 금융 데이터 대신 한국(KRX) 금융 데이터를 공급하는 자율 금융 리서치 에이전트를 구축한다. 단계적 접근(Option A)으로 원본 실행 검증 후 한국화한다.

---

## 디렉토리 구조

```
DEXTER(KOR)/
├── dexter/              ← virattt/dexter 클론 (TypeScript, Bun)
│   └── src/
├── korea-bridge/        ← 한국 금융 데이터 레이어 (Python FastAPI)
│   ├── server.py        ← 메인 FastAPI 서버 (포트 8000)
│   ├── sources/
│   │   ├── fdr.py       ← FinanceDataReader (재무제표, 주가 히스토리)
│   │   ├── pykrx.py     ← KRX 공식 시장 데이터
│   │   └── naver.py     ← 네이버금융 뉴스/공시 스크래핑
│   └── requirements.txt
├── .env                 ← API 키 통합 관리
└── README.md
```

---

## 아키텍처

```
사용자 질문
    ↓
Dexter 에이전트 (TypeScript/Bun)
    ↓ 질문 분해 → 태스크 플래닝
    ↓ 도구 선택
Korea Bridge (Python FastAPI, :8000)
    ├── /financial-statements/{ticker}  → FinanceDataReader
    ├── /stock-price/{ticker}           → pykrx
    └── /news/{ticker}                  → 네이버금융 스크래핑
    ↓
데이터 반환 → Dexter 분석 → 결과 출력
```

---

## 단계별 구현 계획

### Phase 1: 원본 Dexter 실행 (미국 주식으로 검증)
- GitHub 클론
- `.env`에 OpenAI API 키 설정
- `bun install && bun run dev`로 실행 확인
- 검증 쿼리: "Apple의 최근 3년 재무 분석해줘"

### Phase 2: Korea Bridge 구축
- Python FastAPI 서버 생성 (포트 8000)
- 엔드포인트 구현:
  - `GET /financial-statements/{ticker}` — 손익계산서, 대차대조표, 현금흐름표
  - `GET /stock-price/{ticker}` — 주가 히스토리
  - `GET /news/{ticker}` — 최근 뉴스 및 공시
- 종목코드 변환: 한글명("삼성전자") 또는 코드("005930") 모두 허용

### Phase 3: Dexter에 한국 도구 연결
- Dexter tool 정의에 `korean_financial_data` 도구 추가
- Financial Datasets API 호출 부분을 Korea Bridge 호출로 교체
- 검증 쿼리: "삼성전자 최근 실적 분석해줘"

---

## 기술 스택

| 컴포넌트 | 기술 |
|---|---|
| 에이전트 런타임 | TypeScript + Bun 1.3.x |
| LLM | OpenAI GPT-4o |
| 데이터 서버 | Python 3.14 + FastAPI |
| 재무/주가 데이터 | FinanceDataReader, pykrx |
| 뉴스/공시 | 네이버금융 스크래핑 (requests + BeautifulSoup) |

---

## 한국 데이터 소스

| 소스 | 용도 | 비용 |
|---|---|---|
| FinanceDataReader | 재무제표, 주가 히스토리 | 무료 |
| pykrx | KRX 공식 시장 데이터 | 무료 |
| 네이버금융 스크래핑 | 뉴스, 공시, 종목 정보 | 무료 |

---

## 실행 방법

```bash
# 터미널 1: 한국 데이터 서버
cd korea-bridge
pip install -r requirements.txt
python server.py

# 터미널 2: Dexter 에이전트
cd dexter
bun install
bun run dev
```

---

## 데이터 저장소 — Firebase (dexter-kor 전용 프로젝트)

**Firebase 프로젝트:** `dexter-kor` (기존 ske-0004 등과 완전 분리)

**Firestore 구조:**
```
financial_statements/
  {ticker}/
    {year}/        ← 연도별 재무제표 (손익, 대차대조표, 현금흐름)

stock_prices/
  {ticker}/
    {date}/        ← 일별 주가 (캐시, TTL 1일)

news/
  {ticker}/
    {news_id}/     ← 뉴스/공시 (최근 30건)

research_results/
  {result_id}/     ← Dexter 분석 결과 전체 저장 (질문 + 답변 + 사용 도구)
```

**캐시 전략:** 재무제표는 1일 TTL, 주가는 장 종료 후 갱신, 뉴스는 1시간 TTL

---

## 제약 사항

- 포트: Korea Bridge는 `8000` 사용 (3000/8080 금지)
- OpenAI API 키만 있으면 시작 가능 (KIS API 등 유료 키 불필요)
- 네이버금융 스크래핑은 개인 학습/연구 목적으로만 사용
- 실제 투자 매매에 사용 금지 (Dexter 원본 정책 준수)
