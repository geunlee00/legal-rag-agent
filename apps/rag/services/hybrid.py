"""하이브리드 검색: 벡터(dense) + BM25(sparse)를 RRF로 융합.

흐름:
    질문 ─┬→ 벡터 검색(상위 N) ─→ 순위 리스트 A
          └→ BM25 검색(상위 N) ─→ 순위 리스트 B
                   └ RRF 융합 → 최종 top-k
"""

from apps.rag.models import LawChunk
from apps.rag.services.retrieval import search_similar_chunks
from apps.rag.services.keyword_search import search_keyword_ids


def reciprocal_rank_fusion(rank_lists, k_rrf=60):
    """여러 순위 리스트를 RRF로 합쳐 {id: 점수} 반환."""
    scores = {}
    for ranking in rank_lists:
        for rank, doc_id in enumerate(ranking):   # rank: 0,1,2,...
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k_rrf + rank + 1)
    return scores


def hybrid_search(query, k=5, candidates=20):
    """벡터+BM25 하이브리드로 상위 k개 LawChunk 반환."""
    # 1) 각 방식으로 후보 id 순위 리스트 확보
    vec_ids = [c.id for c in search_similar_chunks(query, k=candidates)]
    kw_ids = search_keyword_ids(query, k=candidates)

    # 2) RRF 융합 → 점수 높은 순 top-k id
    fused = reciprocal_rank_fusion([vec_ids, kw_ids])
    if not fused:
        return []
    top_ids = sorted(fused, key=fused.get, reverse=True)[:k]

    # 3) 순서 유지하며 LawChunk 로드 (출처 표시에 law 필요 → select_related)
    id2chunk = {
        c.id: c
        for c in LawChunk.objects.filter(id__in=top_ids).select_related("law")
    }
    result = []
    for i in top_ids:
        c = id2chunk.get(i)
        if c:
            c.score = round(fused[i], 4)   # RRF 점수를 조문에 부착
            result.append(c)
    return result
