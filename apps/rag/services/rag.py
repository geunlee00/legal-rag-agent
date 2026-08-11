"""RAG 파이프라인: 검색된 조문을 근거로 LLM이 답변을 생성한다.

- 검색(retrieval) → 컨텍스트 구성 → LLM 호출 → 답변 + 출처 반환
- 법률 도메인 핵심: '참고 조문에 근거해서만' 답하고 조항을 인용하게 강제한다.
"""

from apps.rag.services.embedding import get_client
from apps.rag.services.retrieval import search_similar_chunks

CHAT_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """당신은 대한민국 개인정보·IT 법령 전문 어시스턴트입니다.
반드시 아래에 제공된 '참고 조문'에 근거해서만 답변하세요.

규칙:
- 답변의 근거가 된 법령명과 조항을 반드시 명시하세요. (예: 개인정보 보호법 제15조)
- 참고 조문에서 확인되지 않는 내용은 추측하지 말고
  "제공된 자료에서 확인할 수 없습니다"라고 답하세요.
- 답변은 한국어로, 간결하고 정확하게 작성하세요."""


def build_context(chunks):
    """검색된 청크들을 LLM에 넣을 텍스트 블록으로 구성."""
    blocks = []
    for c in chunks:
        header = f"[{c.law.name} {c.article_no} {c.article_title}]".strip()
        blocks.append(f"{header}\n{c.content}")
    return "\n\n".join(blocks)


def answer_question(query, k=5):
    """질문 → (답변, 출처 목록) 반환."""
    chunks = search_similar_chunks(query, k=k)

    if not chunks:
        return {"answer": "관련 조문을 찾지 못했습니다.", "sources": []}

    context = build_context(chunks)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"참고 조문:\n{context}\n\n질문: {query}"},
    ]
    resp = get_client().chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0,
    )
    answer = resp.choices[0].message.content

    sources = [
        {
            "law": c.law.name,
            "article_no": c.article_no,
            "article_title": c.article_title,
            "distance": round(getattr(c, "distance", 0.0), 4),
        }
        for c in chunks
    ]
    return {"answer": answer, "sources": sources}
