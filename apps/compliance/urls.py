"""compliance 앱 URL 라우팅."""

from django.urls import path

from apps.compliance.views import DiagnoseView

urlpatterns = [
    # POST /api/compliance/diagnose/  → 회사 프로필 진단
    path("diagnose/", DiagnoseView.as_view(), name="diagnose"),
]
