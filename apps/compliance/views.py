from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.compliance.serializers import CompanyProfileSerializer
from apps.compliance.services.diagnosis import diagnose


class DiagnoseView(APIView):
    """POST: 회사 프로필을 받아 적용 법령을 진단해 돌려준다."""

    def post(self, request):
        # ① 프론트가 보낸 JSON(request.data)을 통역사에 넘긴다
        serializer = CompanyProfileSerializer(data=request.data)

        # ② 유효성 검사. 값이 잘못됐으면 여기서 400 에러를 자동 응답한다.
        serializer.is_valid(raise_exception=True)

        # ③ 검사 통과 → DB에 저장하고, 저장된 모델 객체를 돌려받는다
        profile = serializer.save()

        # ④ 핵심: 저장된 프로필로 적용 법령을 진단한다
        result = diagnose(profile)

        # ⑤ 결과를 JSON으로 응답 (201 = 새로 만들어짐)
        return Response(
            {
                "profile": serializer.data,   # 저장된 회사 정보
                "diagnosis": result,          # 적용 법령 목록
            },
            status=status.HTTP_201_CREATED,
        )
