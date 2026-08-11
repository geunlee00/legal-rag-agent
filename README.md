# 법령 기반 에이전트형 RAG 어시스턴트

개인정보·IT 법령을 근거로, **출처(조항)를 인용해** 답변하는 에이전트형 RAG 서비스입니다.
단순 검색-답변이 아니라 **LangGraph**로 질문을 분류하고, 검색 결과의 충분성을 스스로 평가해
재검색까지 수행하는 **"판단하는" RAG**를 목표로 했습니다.

> 법률 도메인의 핵심 요구사항인 **근거 인용**과 **환각 억제**를 중심으로 설계했습니다.

---

## 주요 특징

- **에이전트형 RAG (CRAG)** — LangGraph로 질문 라우팅 → 검색 → 근거 충분성 자가평가 → 재검색 → 답변
- **하이브리드 검색** — 벡터(pgvector) + 키워드(BM25, 한국어 형태소 분석) 를 RRF로 융합
- **리랭커** — 후보를 관련도로 재정렬해 검색 정밀도 향상
- **근거 인용 & 환각 억제** — 제공된 조문에만 근거해 답변하고 법령·조항을 명시
- **자체 평가 파이프라인** — LLM-as-judge로 context precision·faithfulness 정량 측정

---

## 기술 스택

| 영역 | 기술 |
|---|---|
| 웹/API | Django, Django REST Framework |
| 에이전트 | LangGraph |
| 검색 | pgvector(dense) + BM25/kiwipiepy(sparse), RRF, LLM 리랭커 |
| 벡터 저장 | PostgreSQL + pgvector |
| LLM/임베딩 | OpenAI (gpt-4o-mini, text-embedding-3-small) |
| 인프라 | Docker, docker-compose |
| 데이터 | 국가법령정보센터 Open API |

---

## 아키텍처

### 질의응답 흐름 (LangGraph 에이전트)

```
질문
  │
router ──(잡담)──────────────→ direct_answer → 답변
  │(법령 질문)
retrieve  ← 하이브리드 검색 + 리랭커
  │
grader ──(충분)──────────────→ generate → 근거 인용 답변
  │(부족 & 재시도 여유)
rewrite → retrieve (재검색 루프)
```

### 검색 파이프라인

```
질문 ─┬→ 벡터 검색(pgvector, 상위 30)  ─┐
      └→ BM25 검색(형태소 분석, 상위 30) ─┴─ RRF 융합 → 후보 15
                                              └→ LLM 리랭커 → 최종 top-5
```

---

## 시작하기

### 사전 요구사항
- Python 3.11
- Docker Desktop
- OpenAI API 키, 국가법령정보센터 OC 키

### 설치

```bash
# 1. 가상환경 & 의존성
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt

# 2. 환경변수 설정 (.env.example 복사 후 값 채우기)
cp .env.example .env

# 3. DB(PostgreSQL + pgvector) 실행
docker compose up -d

# 4. 마이그레이션
python manage.py migrate
```

### 데이터 적재

```bash
# 법령 수집 (예: 개인정보/IT 법령)
python manage.py import_laws "개인정보 보호법" "정보통신망 이용촉진 및 정보보호 등에 관한 법률"

# 임베딩 생성
python manage.py embed_chunks
```

### 실행

```bash
python manage.py runserver
```

---

## 사용법

### API

```
POST /api/ask/
{ "question": "가명정보 처리 시 지켜야 할 의무는?", "k": 5 }
```
응답: `answer`(근거 인용 답변) + `sources`(관련 법령·조항)

### 관리 커맨드

```bash
python manage.py ask "..."         # 기본 RAG(벡터) 테스트
python manage.py ask_agent "..."   # 에이전트(하이브리드+리랭커) 테스트
python manage.py eval_llm          # 리랭커 전/후 품질 평가
```

---

## 평가 결과

`eval_llm` 커맨드로 리랭커 적용 전/후를 LLM-judge로 측정 (질문 10개):

| 지표 | Baseline(하이브리드만) | Rerank(리랭커 적용) |
|---|---|---|
| context precision | 0.820 | **0.880** |
| faithfulness | — | **1.000** |

- 리랭커가 관련 조문이 흩어진 어려운 질문에서 검색 정밀도를 개선
- faithfulness 1.0 — 모든 답변이 제공된 조문에 근거 (환각 없음)

---

## 로드맵

- [x] 데이터 파이프라인 (수집·청킹·임베딩)
- [x] 기본 RAG + DRF API
- [x] LangGraph 에이전트 (CRAG)
- [x] 하이브리드 검색 + 리랭커
- [x] 자체 LLM 평가
- [ ] 소형 모델 LoRA 파인튜닝
- [ ] Langfuse 관측(토큰·비용·추적)

---

## 데이터 출처

법령 데이터는 [국가법령정보센터](https://www.law.go.kr) Open API를 통해 수집했습니다.
