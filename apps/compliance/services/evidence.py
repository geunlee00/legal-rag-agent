"""근거보강 (C): 진단된 각 법령에 '실제 조문'을 근거로 붙인다.

diagnose()는 "이 법이 적용된다"까지만 말한다.
여기서는 그 법의 어느 조문 때문인지, 기존 RAG 검색(hybrid_search)으로 찾아 붙인다.

입력  : diagnose() 결과 [{"law", "reason"}, ...]
출력  : 각 항목에 "evidence"(근거 조문 목록)를 추가한 같은 리스트
"""

from apps.rag.services.hybrid import hybrid_search


def add_evidence(diagnosis, per_law=2):
    """진단 결과 각 항목에 근거 조문(evidence)을 붙여 돌려준다."""
    for item in diagnosis:
        # ① 그 법의 의무 내용(reason)을 검색어로 사용
        chunks = hybrid_search(item["reason"], k=10, candidates=30)

        # ② 검색 결과 중 '그 법에 속한 조문'만 근거로 채택
        #    (예: chunk의 법명 "개인정보 보호법" 이
        #         진단 법명 "개인정보 보호법 (민감정보)" 안에 들어있으면 같은 법으로 봄)
        matched = [c for c in chunks if c.law.name in item["law"]]

        # ③ 상위 몇 개만 근거로 첨부
        item["evidence"] = [
            {
                "law": c.law.name,
                "article_no": c.article_no,
                "article_title": c.article_title,
                "content": c.content[:200],   # 미리보기용으로 앞부분만
            }
            for c in matched[:per_law]
        ]
    return diagnosis
