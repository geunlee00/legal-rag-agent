"""RAG Q&A API."""

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.rag.serializers import AskRequestSerializer
from apps.rag.services.agent import answer_question_agent


class AskView(APIView):
    """질문을 받아 LangGraph 에이전트로 근거 기반 답변 + 출처를 반환한다.

    POST /api/ask/
    body: {"question": "...", "k": 5}
    """

    def post(self, request):
        serializer = AskRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        result = answer_question_agent(data["question"], k=data["k"])
        return Response(result)
