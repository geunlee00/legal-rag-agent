"""LLM을 심판(judge)으로 쓰는 자체 평가 지표.

- context_precision: 검색된 조문 중 실제로 질문에 관련된 비율 (리랭커 효과 측정용)
- faithfulness     : 답변이 제공된 조문에 근거하는 정도 (환각 여부, 법률 도메인 핵심)
"""

from apps.rag.services.embedding import get_client

JUDGE_MODEL = "gpt-4o-mini"


def _chat(prompt):
    resp = get_client().chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


def _judge_relevant(question, context):
    """조문 하나가 질문에 관련 있으면 1, 없으면 0."""
    prompt = (
        "아래 조문이 질문에 답하는 데 관련이 있는지 판단하세요.\n"
        "관련 있으면 1, 없으면 0. 숫자 하나만 출력하세요.\n\n"
        f"질문: {question}\n\n조문:\n{context[:600]}"
    )
    return 1 if "1" in _chat(prompt)[:3] else 0


def context_precision(question, contexts):
    """관련 조문 수 / 전체 조문 수 (0~1)."""
    if not contexts:
        return 0.0
    hits = sum(_judge_relevant(question, c) for c in contexts)
    return hits / len(contexts)


def faithfulness(question, answer, contexts):
    """답변이 참고 조문에 근거하는 정도 (0.0~1.0)."""
    joined = "\n\n".join(contexts)
    prompt = (
        "아래 답변이 '참고 조문'에만 근거하는지(내용을 지어내지 않았는지) 평가하세요.\n"
        "0.0(전혀 근거 없음)부터 1.0(완전히 근거함)까지 소수 하나만 출력하세요.\n\n"
        f"질문: {question}\n\n참고 조문:\n{joined}\n\n답변:\n{answer}"
    )
    out = _chat(prompt)
    try:
        return max(0.0, min(1.0, float(out.split()[0])))
    except (ValueError, IndexError):
        return 0.0
