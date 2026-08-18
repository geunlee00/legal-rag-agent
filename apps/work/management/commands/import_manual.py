"""편람 PDF를 적재한다: 로드 → 청킹 → 저장 (임베딩은 embed_docs로 별도).

사용 예:
    python manage.py import_manual docs/administration.pdf --title "2025 행정업무운영 편람"
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.work.models import Document, DocChunk
from apps.work.services.pdf_loader import load_pages
from apps.work.services.chunking import chunk_pages


class Command(BaseCommand):
    help = "편람 PDF를 로드·청킹해 Document/DocChunk로 저장한다."

    def add_arguments(self, parser):
        parser.add_argument("path", help="PDF 파일 경로")
        parser.add_argument("--title", default="행정업무운영 편람", help="문서명")
        parser.add_argument("--source", default="행정안전부", help="출처/발행처")

    @transaction.atomic
    def handle(self, *args, **options):
        pages = load_pages(options["path"])
        self.stdout.write(f"본문 페이지: {len(pages)}개")

        chunks = chunk_pages(pages)
        self.stdout.write(f"청크: {len(chunks)}개")

        # 재적재 시 중복 방지: 같은 제목 문서는 지우고 다시
        Document.objects.filter(title=options["title"]).delete()
        doc = Document.objects.create(
            title=options["title"],
            source=options["source"],
            total_pages=max((p["page"] for p in pages), default=0),
        )

        DocChunk.objects.bulk_create([
            DocChunk(
                document=doc,
                chapter=c.get("chapter", "")[:150],
                section=c.get("section", "")[:250],
                page=c.get("page"),
                content=c["content"],
                order=i,
            )
            for i, c in enumerate(chunks)
        ])
        self.stdout.write(self.style.SUCCESS(f"[완료] {doc.title}: 청크 {len(chunks)}개 저장"))
