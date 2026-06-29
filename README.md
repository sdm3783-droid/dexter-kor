# Dexter KOR

[virattt/dexter](https://github.com/virattt/dexter) 기반 한국 주식 분석 에이전트.

Dexter(TypeScript/Bun) + Korea Bridge(Python FastAPI) 구조로 KRX 데이터를 Dexter 도구로 연결합니다.

---

## 구조

```
dexter/          # virattt/dexter 클론 (Bun + LangChain)
korea-bridge/    # KRX 데이터 제공 FastAPI 서버 (port 8000)
docs/            # 설계 문서
```

### 추가된 Dexter 도구

| 도구 | 설명 |
|------|------|
| `kor_stock_price` | KRX 주가 이력 (1y/2y/3y) |
| `kor_financial_statements` | 재무제표 (매출, 영업이익 등) |
| `kor_news` | 네이버금융 뉴스 헤드라인 |

---

## 사전 요건

- [Bun](https://bun.sh/) 최신 버전
- Python 3.11+
- Anthropic API 키 (또는 OpenAI)
- Firebase 프로젝트 (Firestore Database 활성화)

---

## 설치

### 1. 저장소 클론

```bash
git clone https://github.com/sdm3783-droid/dexter-kor.git
cd dexter-kor
```

### 2. Dexter 클론 (최초 1회)

```bash
git clone https://github.com/virattt/dexter.git dexter
cd dexter
bun install
```

### 3. Korea Bridge 패키지 설치

```bash
cd korea-bridge
pip install -r requirements.txt
```

---

## 환경 설정

### dexter/.env 생성

```env
ANTHROPIC_API_KEY=sk-ant-...
FIREBASE_CREDENTIALS_PATH=./dexter-kor-firebase-adminsdk-fbsvc-XXXXXXXX.json
KOREA_BRIDGE_URL=http://localhost:8000
```

### Firebase 서비스 계정 키

Firebase Console → 프로젝트 설정 → 서비스 계정 → 새 비공개 키 생성  
다운로드한 JSON 파일을 `dexter/` 폴더에 저장

> **주의**: `.gitignore`에 `*firebase-adminsdk*.json`이 포함되어 있어야 합니다.

### Dexter 모델 설정

```bash
# dexter/.dexter/settings.json
{"modelId": "claude-sonnet-4-6", "provider": "anthropic"}
```

또는 Dexter UI에서 `/model` 명령으로 변경 가능합니다.

---

## 실행

### 1. Korea Bridge 서버 시작

```bash
cd korea-bridge
uvicorn server:app --host 0.0.0.0 --port 8000
```

헬스체크: http://localhost:8000/health

### 2. Dexter 시작

```bash
cd dexter
bun run dev
```

---

## 사용 예시

Dexter에서 한국어로 질문하면 자동으로 한국 도구를 사용합니다:

```
삼성전자 최근 1년 주가 추이를 분석해줘

카카오와 네이버의 매출을 비교해줘

SK하이닉스 관련 최신 뉴스 10개 요약해줘
```

---

## Korea Bridge API

| 엔드포인트 | 설명 | 캐시 TTL |
|-----------|------|---------|
| `GET /health` | 상태 확인 | - |
| `GET /stock-price/{ticker}?period=1y` | 주가 이력 | 24h |
| `GET /financial-statements/{ticker}` | 재무제표 | 24h |
| `GET /news/{ticker}?limit=10` | 뉴스 | 1h |

`ticker`는 종목명(삼성전자) 또는 6자리 코드(005930) 모두 가능합니다.

---

## 주의사항

- 네이버금융 스크래핑은 **개인 학습/연구 목적 전용**
- 실제 투자 매매에 사용 금지
- Firebase 서비스 계정 JSON은 절대 공개 저장소에 커밋하지 않을 것
