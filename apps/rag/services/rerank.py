"""LLM 기반 리랭커.

하이브리드 검색으로 뽑은 후보들을 질문과의 관련도로 재정렬해
상위 top_k개만 남긴다. (추가 의존성 없이 OpenAI로 처리)

- 크로스인코더(bge-reranker 등)로 교체 가능하도록 rerank() 인터페이스만 맞추면 됨.
"""

import json

from apps.rag.services.embedding import get_client

RERANK_MODEL = "gpt-4o-mini"


def _parse_order(text, n):
    """LLM이 낸 '[3, 0, 5]' 같은 배열을 유효한 인덱스 순서로 정규화."""
    try:
        arr = json.loads(text[text.index("["): text.rindex("]") + 1])
    except Exception:
        return list(range(n))

    order = []
    for x in arr:
        if isinstance(x, int) and 0 <= x < n and x not in order:
            order.append(x)
    # LLM이 빠뜨린 인덱스는 뒤에 붙여 안전하게 보완
    for i in range(n):
        if i not in order:
            order.append(i)
    return order


def rerank(query, chunks, top_k=5):
    """후보 chunks를 질문 관련도순으로 재정렬해 상위 top_k개 반환."""
    if not chunks:
        return []

    listing = []
    for idx, c in enumerate(chunks):
        snippet = c.content[:300].replace("\n", " ")
        listing.append(f"[{idx}] {c.law.name} {c.article_no} {c.article_title}: {snippet}")
    catalog = "\n".join(listing)

    prompt = (
        f"질문: {query}\n\n"
        f"아래 후보 조문들을 질문과의 관련도가 높은 순으로 정렬하세요.\n"
        f"관련도 높은 상위 {top_k}개의 번호만 JSON 배열로 출력하세요. 예: [3, 0, 5]\n"
        f"설명 없이 배열만 출력하세요.\n\n후보:\n{catalog}"
    )
    resp = get_client().chat.completions.create(
        model=RERANK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    order = _parse_order(resp.choices[0].message.content, len(chunks))

    reranked = [chunks[i] for i in order[:top_k]]
    # 리랭크 순위를 점수로 부착 (1등=1.0에 가깝게)
    n = max(len(reranked), 1)
    for rank, c in enumerate(reranked):
        c.score = round(1.0 - rank / n, 4)
    return reranked
