from django.db import models
from pgvector.django import VectorField, HnswIndex


class Document(models.Model):
    """편람 등 원본 문서 메타데이터."""
    title = models.CharField("문서명", max_length=255)
    source = models.CharField("출처/발행처", max_length=255, blank=True)
    total_pages = models.PositiveIntegerField("총 페이지", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class DocChunk(models.Model):
    """검색 단위(절/항). 임베딩 + 인용정보(장·절·페이지) 보관."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    chapter = models.CharField("장", max_length=150, blank=True)       # 예: 제2장 공문서 관리
    section = models.CharField("절/항 제목", max_length=250, blank=True)  # 예: 제1절 공문서의 작성 > 6. 문서의 기안
    page = models.PositiveIntegerField("페이지", null=True, blank=True)
    content = models.TextField("본문")
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    order = models.PositiveIntegerField("정렬순서", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            HnswIndex(
                name="docchunk_emb_hnsw",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]

    def __str__(self):
        return f"{self.section or self.chapter} (p.{self.page})".strip()
