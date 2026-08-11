"""LangGraph 기반 에이전트형 RAG (CRAG 패턴).

흐름:
    START → route ─(chitchat)→ direct_answer → END
                 └(legal)→ retrieve → grade ─(sufficient)→ generate → END
                                          └(insufficient & 재시도 여유)→ rewrite → retrieve ↺

노드:
    route         : 법령 질문 / 잡담 분류        ← 직접 구현
    retrieve      : 벡터 검색 (2단계 함수 재사용)
    grade         : 검색 결과 충분성 자가평가       ← 직접 구현
    rewrite       : 질문 재작성 후 재검색
    generate      : 근거 기반 최종 답변 + 출처
    direct_answer : 잡담 등 검색 없이 바로 답변
"""

from typing import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from apps.rag.services.hybrid import hybrid_search
from apps.rag.services.rerank import rerank
from apps.rag.services.rag import build_context, SYSTEM_PROMPT

MAX_ATTEMPTS = 2  # 재검색(rewrite) 최대 횟수
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


class AgentState(TypedDict):
    question: str      # 원 질문
    query: str         # 실제 검색에 쓰는 질문 (rewrite로 바뀔 수 있음)
    k: int             # 검색 개수
    route: str         # "legal" | "chitchat"
    documents: list    # 검색된 LawChunk 리스트
    grade: str         # "sufficient" | "insufficient"
    attempts: int      # 재검색 횟수
    answer: str        # 최종 답변
    sources: list      # 출처 목록


# ========== 노드 ==========

def route_node(state):
    """법령 질문인지 잡담인지 분류해 state['route']를 채운다."""
    prompt = (
        "다음 사용자 입력이 '대한민국 개인정보·IT 법령'에 관한 질문인지 판단하세요.\n"
        "법령·규정·처벌·의무·권리 등에 관한 질문이면 legal, "
        "인사말·잡담·법령과 무관하면 chitchat 이라고만 답하세요.\n\n"
        f"입력: {state['question']}"
    )
    decision = llm.invoke(prompt).content.strip().lower()
    route = "legal" if "legal" in decision else "chitchat"
    return {"route": route}


def retrieve_node(state):
    k = state.get("k", 5)
    candidates = hybrid_search(state["query"], k=15, candidates=30)  # 넉넉히 후보 확보
    docs = rerank(state["query"], candidates, top_k=k)               # 관련도로 재정렬
    return {"documents": docs}


def grade_node(state):
    """검색된 조문이 질문에 충분한지 평가해 state['grade']를 채운다."""
    context = build_context(state["documents"])
    prompt = (
        "아래 '참고 조문'이 사용자 질문에 답하기에 충분한 근거를 담고 있는지 판단하세요.\n"
        "충분하면 sufficient, 부족하거나 관련이 없으면 insufficient 라고만 답하세요.\n\n"
        f"질문: {state['question']}\n\n참고 조문:\n{context}"
    )
    decision = llm.invoke(prompt).content.strip().lower()
    # 주의: 'sufficient'는 'insufficient'의 부분문자열 → insufficient를 먼저 검사
    grade = "insufficient" if "insufficient" in decision else "sufficient"
    return {"grade": grade}


def rewrite_node(state):
    prompt = (
        "다음 질문을 법령 검색에 더 적합하도록 핵심 키워드 중심으로 재작성하세요. "
        "설명 없이 재작성된 질문만 출력하세요.\n\n질문: " + state["question"]
    )
    new_query = llm.invoke(prompt).content.strip()
    return {"query": new_query, "attempts": state.get("attempts", 0) + 1}


def generate_node(state):
    docs = state["documents"]
    if not docs:
        return {"answer": "제공된 자료에서 확인할 수 없습니다.", "sources": []}

    context = build_context(docs)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"참고 조문:\n{context}\n\n질문: {state['question']}"},
    ]
    answer = llm.invoke(messages).content
    sources = [
        {
            "law": d.law.name,
            "article_no": d.article_no,
            "article_title": d.article_title,
            "score": round(getattr(d, "score", 0.0), 4),
        }
        for d in docs
    ]
    return {"answer": answer, "sources": sources}


def direct_answer_node(state):
    answer = llm.invoke(state["question"]).content
    return {"answer": answer, "sources": []}


# ========== 분기(라우팅) 함수 ==========

def route_decision(state):
    return "retrieve" if state.get("route") == "legal" else "direct_answer"


def grade_decision(state):
    if state.get("grade") == "sufficient":
        return "generate"
    if state.get("attempts", 0) >= MAX_ATTEMPTS:
        return "generate"   # 재시도 소진 → 있는 자료로라도 답변
    return "rewrite"


# ========== 그래프 배선 ==========

def build_agent():
    g = StateGraph(AgentState)
    g.add_node("router", route_node)
    g.add_node("retrieve", retrieve_node)
    g.add_node("grader", grade_node)
    g.add_node("rewrite", rewrite_node)
    g.add_node("generate", generate_node)
    g.add_node("direct_answer", direct_answer_node)

    g.add_edge(START, "router")
    g.add_conditional_edges("router", route_decision,
                            {"retrieve": "retrieve", "direct_answer": "direct_answer"})
    g.add_edge("retrieve", "grader")
    g.add_conditional_edges("grader", grade_decision,
                            {"generate": "generate", "rewrite": "rewrite"})
    g.add_edge("rewrite", "retrieve")
    g.add_edge("generate", END)
    g.add_edge("direct_answer", END)
    return g.compile()


agent = build_agent()


def answer_question_agent(question, k=5):
    """에이전트 실행 → {answer, sources} 반환. (뷰/커맨드에서 호출)"""
    final = agent.invoke({
        "question": question,
        "query": question,
        "k": k,
        "attempts": 0,
    })
    return {"answer": final["answer"], "sources": final.get("sources", [])}
