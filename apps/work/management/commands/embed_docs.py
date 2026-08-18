"""DocChunk에 임베딩을 채운다 (rag 앱의 임베딩 서비스 재사용).

사용 예:
    python manage.py embed_docs
    python manage.py embed_docs --batch 50
"""

from django.core.management.base import BaseCommand

from apps.work.models import DocChunk
from apps.rag.services.embedding import embed_texts   # 엔진 공유


class Command(BaseCommand):
    help = "임베딩이 없는 DocChunk에 임베딩을 생성해 채운다."

    def add_arguments(self, parser):
        parser.add_argument("--batch", type=int, default=100)
        parser.add_argument("--all", action="store_true", help="이미 있는 것도 다시 생성")

    def handle(self, *args, **options):
        qs = DocChunk.objects.all() if options["all"] else DocChunk.objects.filter(embedding__isnull=True)
        ids = list(qs.order_by("id").values_list("id", flat=True))
        total = len(ids)
        if total == 0:
            self.stdout.write("임베딩할 청크가 없습니다.")
            return

        self.stdout.write(f"대상 청크: {total}개")
        batch = options["batch"]
        done = 0
        for i in range(0, total, batch):
            objs = list(DocChunk.objects.filter(id__in=ids[i:i + batch]))
            vectors = embed_texts([o.content for o in objs])
            for o, v in zip(objs, vectors):
                o.embedding = v
            DocChunk.objects.bulk_update(objs, ["embedding"])
            done += len(objs)
            self.stdout.write(f"  {done}/{total} 완료")

        self.stdout.write(self.style.SUCCESS(f"임베딩 완료: {done}개"))
