"""벡터 유사도 검색 (RAG의 R = Retrieval).

★ 이 파일의 search_similar_chunks()는 당신이 직접 구현합니다. (2-1의 핵심)

아이디어:
    1) 질문(query)을 임베딩해서 질문 벡터를 얻는다
    2) pgvector의 코사인 거리로 가장 가까운 조문 청크 k개를 DB에서 찾는다
"""


from pgvector.django import CosineDistance

from apps.rag.models import LawChunk
from apps.rag.services.embedding import embed_texts


def search_similar_chunks(query, k=5):
    """query와 의미가 가까운 LawChunk를 거리 오름차순으로 k개 반환."""
    query_vector = embed_texts([query])[0]          # ① 질문을 벡터로
    return list(
        LawChunk.objects
        .exclude(embedding__isnull=True)             # 임베딩 있는 것만
        .annotate(distance=CosineDistance("embedding", query_vector))  # ② 거리 계산
        .select_related("law")                       # 출처(법령명) 함께 로드 (N+1 방지)
        .order_by("distance")[:k]                    # ③ 가까운 순 k개
    )
