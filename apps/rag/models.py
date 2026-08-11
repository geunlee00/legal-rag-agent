from django.db import models
from pgvector.django import VectorField, HnswIndex


class Law(models.Model):
    """법령 메타데이터."""
    law_id = models.CharField("법령ID", max_length=50, unique=True)
    name = models.CharField("법령명", max_length=255)
    department = models.CharField("소관부처", max_length=100, blank=True)
    promulgation_date = models.DateField("공포일자", null=True, blank=True)
    enforcement_date = models.DateField("시행일자", null=True, blank=True)
    source_url = models.URLField("출처", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class LawChunk(models.Model):
    """검색 단위(조). 임베딩 + 인용정보 보관."""
    law = models.ForeignKey(Law, on_delete=models.CASCADE, related_name="chunks")
    article_no = models.CharField("조번호", max_length=20, blank=True)
    article_title = models.CharField("조제목", max_length=255, blank=True)
    content = models.TextField("본문")
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    order = models.PositiveIntegerField("정렬순서", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            HnswIndex(
                name="lawchunk_emb_hnsw",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]

    def __str__(self):
        return f"{self.law.name} {self.article_no}".strip()