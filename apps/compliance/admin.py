from django.contrib import admin

from apps.compliance.models import CompanyProfile


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "industry", "business_type", "employee_count", "created_at")
    list_filter = ("industry", "business_type")
    search_fields = ("name",)
