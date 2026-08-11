"""rag 앱 URL 라우팅."""

from django.urls import path

from apps.rag.views import AskView

urlpatterns = [
    path("ask/", AskView.as_view(), name="ask"),
]
