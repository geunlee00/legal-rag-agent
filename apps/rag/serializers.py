"""API 입출력 검증용 시리얼라이저."""

from rest_framework import serializers


class AskRequestSerializer(serializers.Serializer):
    """POST /api/ask 요청 검증."""
    question = serializers.CharField(min_length=1, trim_whitespace=True)
    k = serializers.IntegerField(required=False, default=5, min_value=1, max_value=20)
