"""LangGraph 에이전트로 질문에 답하는 테스트 커맨드.

사용 예:
    python manage.py ask_agent "가명정보 처리 시 지켜야 할 의무는?"
    python manage.py ask_agent "안녕? 오늘 기분 어때?"   # 잡담 → 검색 없이 응답
"""

from django.core.management.base import BaseCommand

from apps.rag.services.agent import answer_question_agent


class Command(BaseCommand):
    help = "LangGraph 에이전트형 RAG로 답변을 생성한다."

    def add_arguments(self, parser):
        parser.add_argument("question", help="질문 문장")
        parser.add_argument("--k", type=int, default=5, help="검색할 조문 수")

    def handle(self, *args, **options):
        result = answer_question_agent(options["question"], k=options["k"])

        self.stdout.write("\n=== 답변 ===")
        self.stdout.write(result["answer"])

        self.stdout.write("\n=== 출처 ===")
        if not result["sources"]:
            self.stdout.write("(검색 없이 답변)")
        for s in result["sources"]:
            self.stdout.write(
                f"- {s['law']} {s['article_no']} {s['article_title']} (관련도 {s['score']})"
            )
