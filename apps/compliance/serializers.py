from rest_framework import serializers

from apps.compliance.models import CompanyProfile


class CompanyProfileSerializer(serializers.ModelSerializer):
    """CompanyProfile <-> JSON 통역사.

    ModelSerializer: 모델을 보고 필드를 자동으로 만들어 준다.
    (name, industry, handles_personal_data ... 를 우리가 다시 안 적어도 됨)
    """

    class Meta:
        model = CompanyProfile        # 어떤 모델을 번역할지
        fields = "__all__"            # 모델의 모든 필드를 포함
        read_only_fields = ["id", "created_at"]  # 서버가 정하는 값 (입력 못 받게)
