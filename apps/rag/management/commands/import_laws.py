"""법령 수집 커맨드.

사용 예:
    python manage.py import_laws "개인정보 보호법" "정보통신망 이용촉진 및 정보보호 등에 관한 법률"

동작:
    1) 법령명으로 검색해 정확히 일치하는 법령을 찾음
    2) 본문(조문) 조회
    3) Law 저장 + 조문을 parse_articles()로 청크화해 LawChunk 저장
       (임베딩은 이후 단계 1-d에서 별도로 채움)
"""

from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.rag.models import Law, LawChunk
from apps.rag.services import law_api
from apps.rag.services.parsing import parse_articles


def _parse_date(s):
    """'20251002' 형태 문자열을 date로. 형식이 아니면 None."""
    s = (s or "").strip()
    if len(s) == 8 and s.isdigit():
        return datetime.strptime(s, "%Y%m%d").date()
    return None


class Command(BaseCommand):
    help = "국가법령정보센터에서 법령을 수집해 Law/LawChunk로 저장한다."

    def add_arguments(self, parser):
        parser.add_argument("names", nargs="+", help="수집할 법령명 (공백으로 여러 개)")

    def handle(self, *args, **options):
        for name in options["names"]:
            try:
                self._import_one(name)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[실패] {name}: {e}"))

    @transaction.atomic
    def _import_one(self, name):
        results = law_api.search_laws(name, display=5)
        if not results:
            self.stdout.write(self.style.WARNING(f"[건너뜀] 검색 결과 없음: {name}"))
            return

        # 법령명이 정확히 일치하는 것 우선, 없으면 첫 결과
        match = next((r for r in results if r.get("법령명한글") == name), results[0])

        mst = match["법령일련번호"]
        body = law_api.get_law_body(mst)

        law, _ = Law.objects.update_or_create(
            law_id=match["법령ID"],
            defaults={
                "name": match["법령명한글"],
                "department": match.get("소관부처명", ""),
                "promulgation_date": _parse_date(match.get("공포일자")),
                "enforcement_date": _parse_date(match.get("시행일자")),
                "source_url": f"https://www.law.go.kr/법령/{match['법령명한글']}",
            },
        )

        # 재수집 시 중복 방지: 기존 청크 삭제 후 재삽입
        law.chunks.all().delete()

        articles = parse_articles(body)  # ← 직접 구현한 핵심 파싱
        chunks = [
            LawChunk(
                law=law,
                article_no=a["article_no"],
                article_title=a["article_title"],
                content=a["content"],
                order=i,
            )
            for i, a in enumerate(articles)
        ]
        LawChunk.objects.bulk_create(chunks)
        self.stdout.write(self.style.SUCCESS(f"[완료] {law.name}: 조문 {len(chunks)}개 저장"))
