# 법령·판례 RAG 어시스턴트 — 개발 문서

> 법령/판례 문서를 기반으로, 출처(조항)를 인용해 답변하는 에이전트형 RAG 서비스.
> 이 문서는 개발환경·기술스택·의사결정을 기록하며, 변경 시 함께 수정한다.

- **최종 수정일**: 2026-08-11
- **도메인**: 법률 (국가법령정보센터 등 공개 데이터 활용)
- **LLM 전략**: API 우선 → 파인튜닝은 확장 과제

---

## 1. 개발환경

| 항목 | 값 | 비고 |
|---|---|---|
| OS | Windows 11 Pro | |
| Shell | PowerShell | |
| Python | 3.11.9 | 3.13은 일부 ML 라이브러리 호환 이슈로 회피 |
| 가상환경 | `.venv/` | 활성화: `.\.venv\Scripts\Activate.ps1` |
| Django | 5.2.17 | |
| Docker | Engine v29.6.1 / Compose v5.1.4 | Docker Desktop 필요 |
| IDE | PyCharm | |

---

## 2. 기술 스택

| 계층 | 기술 | 역할 |
|---|---|---|
| 웹/API | Django + DRF | 인증, 대화 세션, 스트리밍 응답 |
| 에이전트 | LangGraph | 질문 라우팅 → 검색 → 검증 → 생성 → 자기수정(CRAG) |
| 검색 | 하이브리드(BM25 + 벡터) + 리랭커 | RAG 검색 품질 |
| 벡터 저장 | PostgreSQL + pgvector | 임베딩 저장/유사도 검색 |
| LLM | OpenAI API (GPT) | 답변 생성 — 파인튜닝은 나중 |
| 임베딩 모델 | OpenAI `text-embedding-3-small` (1536차원) | API 방식, 저렴·안정 |
| 비동기 처리 | Celery + Redis | 문서 수집·청킹·임베딩 (2단계~) |
| 관측 | Langfuse 또는 LangSmith | 토큰/비용/추적 |
| 평가 | RAGAS | 검색·답변 품질 정량 평가 |
| 배포/재현 | Docker, docker-compose | 환경 재현성 |

---

## 3. 프로젝트 구조

```
solo_project/
├── .venv/                  # 가상환경
├── .env                    # 비밀값 (git 제외)
├── .gitignore
├── docker-compose.yml      # Postgres + pgvector
├── requirements.txt
├── manage.py
├── DEVELOPMENT.md          # (이 문서)
├── solo_project/           # Django 설정 패키지 (config 역할)
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py / asgi.py
├── templates/
└── apps/
    └── rag/                # 첫 앱 (RAG 로직)
```

---

## 4. 로컬 실행 방법

```bash
# 1. 가상환경 활성화
.\.venv\Scripts\Activate.ps1

# 2. 의존성 설치
pip install -r requirements.txt

# 3. DB 컨테이너 실행 (Docker Desktop 켜져 있어야 함)
docker compose up -d

# 4. 마이그레이션
python manage.py migrate

# 5. 서버 실행
python manage.py runserver
# → http://127.0.0.1:8000
```

### 자주 쓰는 Docker 명령
```bash
docker compose ps       # 컨테이너 상태
docker compose down     # 정지 (데이터는 volume 유지)
docker compose logs db  # DB 로그 (연결 문제 디버깅)
```

---

## 5. 데이터베이스

- **엔진**: PostgreSQL 16 (`pgvector/pgvector:pg16` 이미지)
- **DB / 계정**: `legal_rag` / `rag_user` / `rag_pass` (로컬 개발용, `.env`와 일치)
- **포트**: 5432

### .env 예시
```
SECRET_KEY=django-insecure-dev-change-me
DEBUG=True
DB_NAME=legal_rag
DB_USER=rag_user
DB_PASSWORD=rag_pass
DB_HOST=localhost
DB_PORT=5432
```

---

## 6. 로드맵

| 단계 | 내용 | 상태 |
|---|---|---|
| 0 | Django+DRF+Docker+pgvector 뼈대 | ✅ 완료 |
| 1 | 법령 데이터 수집→청킹→임베딩→저장 파이프라인 | ✅ 완료 |
| 2 | 기본 RAG Q&A (검색 + API 답변) | ✅ 완료 |
| 3 | LangGraph 에이전트화 (라우팅 + CRAG 폴백) | ✅ 완료 |
| 4 | 하이브리드 검색 + 리랭커로 정확도 개선 | ✅ 완료 |
| 5 | 검색 품질 평가 (자체 LLM-judge) | ✅ 완료 (5-a) / Langfuse 관측은 보류 |
| 6 | (확장) 소형 모델 LoRA 파인튜닝 실험 | 예정 |

---

## 7. 기술 선택 기록 (의사결정 로그)

### PostgreSQL + pgvector (vs MySQL / 전용 벡터 DB)
- `pgvector`는 PostgreSQL 전용 확장. MySQL의 벡터 기능은 아직 초기 단계라 생태계·자료가 빈약.
- 전용 벡터 DB(Qdrant 등) 대신 pgvector를 택한 이유: 메인 DB와 벡터를 **하나의 인프라**로 통합 → 복잡도 감소, 원문·조항번호와 벡터가 같은 테이블에 있어 **출처 인용**이 쉬움. 개인 프로젝트 규모엔 성능도 충분.
- 확장 시나리오: 데이터 대규모화 시 Qdrant 이관 검토 (면접용 스토리).

### LLM: API 우선 (OpenAI)
- 초기 개발 속도·품질 확보를 위해 OpenAI API 사용. 파인튜닝(LoRA/QLoRA)은 별도 확장 과제로 후순위.

### 임베딩: OpenAI text-embedding-3-small
- 로컬 모델(BGE-m3) 대신 API 선택. 이유: 이미 OpenAI 크레딧 보유, 설치·GPU 부담 없이 간단, 품질 안정적.
- `small`(1536차원) 선택: 개인 프로젝트 규모엔 품질 충분하고 `large`(3072) 대비 저렴. → **pgvector 컬럼 차원 = 1536** 으로 고정.

### Django 설정 패키지명 = `solo_project`
- PyCharm이 프로젝트명으로 생성. 일반적인 `config` 대신 `solo_project.settings` / `solo_project.urls` 사용.

---

## 8. 변경 이력

- 2026-08-11: 문서 최초 작성 (0단계 세팅 진행 중)
- 2026-08-11: 0단계 완료 — Django+DRF+Postgres(pgvector) 뼈대 구동 확인(로켓 화면). 1단계 착수.
- 2026-08-11: 임베딩=OpenAI text-embedding-3-small(1536차원), LLM=OpenAI 확정. 1-a(pgvector 확장+스키마) 시작.
- 2026-08-11: 도메인=개인정보/IT 확정. 국가법령정보센터 OC 발급·설정. 1-a 완료(rag_law/rag_lawchunk 테이블, vector 확장 확인).
- 2026-08-11: 1단계 완료 — 개인정보/IT 법령 8개 수집(조문 589개), 조문 파싱(항/호/목 병합), OpenAI 임베딩 589/589(1536차원) 채움. import_laws·embed_chunks 커맨드 구현. 2단계 착수.
- 2026-08-11: 2-1 완료 — pgvector 코사인 유사도 검색(retrieval) + gpt-4o-mini 근거기반 답변(rag) 구현. `manage.py ask`로 조항 인용 답변 확인.
- 2026-08-11: 2단계 완료 — DRF API(POST /api/ask/) 노출. 시리얼라이저 입력검증 + 서비스 계층 분리. 3단계(LangGraph) 착수.
- 2026-08-11: 3단계 완료 — LangGraph CRAG 에이전트 구현(router/retrieve/grader/rewrite/generate/direct_answer). 노드명↔상태키 충돌(route/grade) → router/grader로 해결. AskView를 에이전트로 교체. 잡담=검색생략, 법령질문=검색·채점·재검색 확인.
- 2026-08-11: 4단계 완료 — 하이브리드 검색(pgvector + kiwipiepy 형태소 BM25, RRF 융합) + LLM 리랭커(후보30→15→top5). 한국어 FTS 한계 실험으로 BM25 채택 근거 확보. retrieve_node가 hybrid→rerank 흐름. 출처 품질 개선(무관 조문 배제) 확인.
- 2026-08-11: 5-a 착수. RAGAS 설치가 langchain을 1.x/openai 2.x로 강제 업그레이드 → ragas 자체 임포트 실패(의존성 충돌). 결정: **RAGAS 대신 자체 LLM-judge 평가** 채택. 앱 의존성은 안정 버전(openai 1.x, langgraph 0.2)으로 롤백, pip check 통과.
- 2026-08-11: 5-a 완료 — 자체 LLM-judge 평가 구현(context precision, faithfulness) + eval_llm 커맨드로 리랭커 전/후 비교. 2문항 검증: CP 0.90→1.00, faithfulness 1.00. Langfuse 관측(5-b)은 보류.
- 2026-08-11: 전체 10문항 평가 결과 — context precision baseline 0.820 → rerank 0.880(+6pp), faithfulness 1.000. 관찰: 리랭커가 어려운 질문(Q3·Q4: 0.4~0.6→0.8)에서 크게 개선하나, 이미 완벽했던 일부(Q7·Q8: 1.0→0.8)는 소폭 하락 → **개선 여지**: 리랭커 품질/프롬프트 튜닝, 또는 grade가 부실할 때만 리랭크하는 조건부 적용 검토.

## 9. 다음 할 일 (내일)
- (선택) 리랭커 튜닝: Q7·Q8 하락 원인 분석, 프롬프트/조건부 리랭크 검토
- README 작성 + 아키텍처 문서화 (면접/포트폴리오용)
- git 커밋 정리
- (여유 시) 6단계 LoRA 파인튜닝 — **RunPod에서 진행 예정(크레딧 ~$10)** → 예산상 소형 모델 QLoRA 단기 학습으로 설계
- (여유 시) Langfuse 관측(5-b)
