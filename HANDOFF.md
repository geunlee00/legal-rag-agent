# 이어가기 요약 (새 채팅용 핸드오프)

> 새 채팅을 열고 이 파일 내용을 붙여넣거나, "DEVELOPMENT.md와 메모리 읽고 이어가자"라고 하면 됩니다.
> (같은 프로젝트면 메모리는 자동 로드됨)

## 이 프로젝트가 뭔지
- 위치: `C:\solo_workspace\solo_project` (Django, Windows, .venv)
- **두 갈래**:
  1. **완성된 솔로 포트폴리오** — 「법령 RAG 어시스턴트」(개인정보/IT 법령). 0~5단계 완료.
  2. **새 솔로 프로젝트 아이디어** — 위 엔진을 확장한 "규제 RAG 자동진단". 기획 단계.

## ① 법령 RAG 포트폴리오 — 현재 상태
- **완료(0~5단계)**: Django+DRF+Docker(pgvector) / 법령 8개·조문 589개 수집·임베딩 / 벡터검색 RAG + DRF API(`POST /api/ask/`) / LangGraph CRAG 에이전트 / 하이브리드검색(BM25+벡터 RRF)+LLM 리랭커 / 자체 LLM 평가(context precision 0.82→0.88, faithfulness 1.0).
- 스택: OpenAI(gpt-4o-mini, text-embedding-3-small 1536), pgvector, kiwipiepy, LangGraph 0.2.
- 상세: `DEVELOPMENT.md` 참조.
- **남은 마무리**: git 커밋/푸시(레포명 예: legal-rag-agent), README 있음, .idea 추적해제(`git rm -r --cached .idea`), (선택)리랭커 튜닝.
- **parked**: `apps/work` 편람(행안부 PDF) — pdf_loader 완료, `chunk_pages` 스텁 미구현.

## ② 새 솔로 프로젝트(규제 RAG) — 기획 결정사항
- **팀 파이널 아님 → 본인 솔로 프로젝트로 진행** (필수요건 MCP·멀티에이전트·ML은 선택/확장).
- **도메인 후보 2개** (기획서 파일 있음):
  - `FINAL_PLAN_1_기업규제.md` — 기업 규제·입법 모니터링&영향분석(폴리시레이더). B2B, FiscalNote/Quorum 모델.
  - `FINAL_PLAN_2_부동산.md` — 부동산 규제·세금 자동진단(집파일럿). 소비자.
- **솔로엔 2안(부동산) 추천**: 법령 데이터 신선, 계산결과 가시적, 혼자 데모 쉬움.
- 공통 컨셉: "질문답변 챗봇 아님 → 요청→자동 처리→**근거 인용 리포트 산출**"(업무자동화).

## 데이터/기술 핵심 팩트
- **법령(law.go.kr, OC키)**: 현행법령 5,607건. **최신 유지 잘 됨**(시행일자로 시행예정도 커버). = 기준 데이터.
- **의안(열린국회 open.assembly.go.kr, 별도키)**: 2단계(의안정보 통합 API=메타 → 법률안주요내용 API=SUMMARY 본문). 21대 26,721건. **배치 지연 있음**.
- `likms.assembly.go.kr`: robots.txt로 일반 크롤링 **전면 금지**(네이버봇만) → 크롤링 말고 Open API 사용.
- 최신성 = 증분 동기화(update_or_create + embedding__isnull 델타임베딩 + is_current/effective_date 현행필터 + cron).

## 솔로 MVP 순서 (부동산 기준)
1. 세법·규제 법령 수집·임베딩 (엔진 재사용)
2. 상황 입력 → RAG 근거 검색 (있음)
3. 규칙기반 세금 계산 (취득세/양도세부터)
4. 근거 인용 진단 리포트
5. 간단 웹 화면
→ 이후 확장: 멀티에이전트·모니터링·대출·ML분류

## 작업 방식 (중요)
- 보일러플레이트는 AI가 파일로 작성, **핵심 로직(파싱·검색·판단)은 사용자가 직접 타이핑**(스텁으로 남김).
- 단계마다 DEVELOPMENT.md 로드맵/변경이력 갱신.

## 참고 파일
- `DEVELOPMENT.md` (포트폴리오 상세·의사결정·이력)
- `FINAL_PLAN_1_기업규제.md`, `FINAL_PLAN_2_부동산.md` (기획서)
- 메모리: `legal-rag-project`, `final-project-practice`
