"""터미널에서 RAG Q&A를 빠르게 테스트하는 커맨드.

사용 예:
    python manage.py ask "개인정보를 수집하려면 어떤 요건이 필요해?"
    python manage.py ask "영상정보처리기기 설치 제한은?" --k 3
"""

from django.core.management.base import BaseCommand

from apps.rag.services.rag import answer_question


class Command(BaseCommand):
    help = "질문에 대해 관련 법령 조문을 검색하고 근거 기반 답변을 생성한다."

    def add_arguments(self, parser):
        parser.add_argument("question", help="질문 문장")
        parser.add_argument("--k", type=int, default=5, help="검색할 조문 수")

    def handle(self, *args, **options):
        result = answer_question(options["question"], k=options["k"])

        self.stdout.write("\n=== 답변 ===")
        self.stdout.write(result["answer"])

        self.stdout.write("\n=== 출처 ===")
        for s in result["sources"]:
            self.stdout.write(
                f"- {s['law']} {s['article_no']} {s['article_title']} (거리 {s['distance']})"
            )
