"""LawChunk에 임베딩을 채우는 커맨드.

사용 예:
    python manage.py embed_chunks           # 임베딩이 비어있는 것만
    python manage.py embed_chunks --all      # 전체 재생성
    python manage.py embed_chunks --batch 50 # 배치 크기 조정

동작:
    임베딩이 없는 청크를 배치로 묶어 OpenAI에 요청하고,
    받은 벡터를 bulk_update로 저장한다.
"""

from django.core.management.base import BaseCommand

from apps.rag.models import LawChunk
from apps.rag.services.embedding import embed_texts


class Command(BaseCommand):
    help = "임베딩이 없는 LawChunk에 임베딩을 생성해 채운다."

    def add_arguments(self, parser):
        parser.add_argument("--batch", type=int, default=100, help="한 번에 요청할 청크 수")
        parser.add_argument("--all", action="store_true", help="이미 채워진 것도 다시 생성")

    def handle(self, *args, **options):
        qs = LawChunk.objects.all() if options["all"] else LawChunk.objects.filter(embedding__isnull=True)
        ids = list(qs.order_by("id").values_list("id", flat=True))
        total = len(ids)
        if total == 0:
            self.stdout.write("임베딩할 청크가 없습니다.")
            return

        self.stdout.write(f"대상 청크: {total}개")
        batch = options["batch"]
        done = 0
        for i in range(0, total, batch):
            objs = list(LawChunk.objects.filter(id__in=ids[i:i + batch]))
            vectors = embed_texts([o.content for o in objs])
            for o, v in zip(objs, vectors):
                o.embedding = v
            LawChunk.objects.bulk_update(objs, ["embedding"])
            done += len(objs)
            self.stdout.write(f"  {done}/{total} 완료")

        self.stdout.write(self.style.SUCCESS(f"임베딩 완료: {done}개"))
