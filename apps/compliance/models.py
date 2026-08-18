from django.db import models


class CompanyProfile(models.Model):
    """회사가 입력하는 프로필. '적용법령 진단'의 입력값이 된다.

    설계 의도:
        - 여기 담긴 각 항목(업종·취급 데이터 종류 등)이 Step 2의
          '규칙 매핑'에서 특정 법령으로 연결된다.
          예) handles_sensitive_data=True  → 개인정보보호법(민감정보) 적용
              does_online_sales=True       → 전자상거래법 적용
        - 그래서 판정에 필요한 신호를 '구조화된 필드'로 명확히 나눠 담는다.
          (자유서술 대신 boolean/choices → Step 2 규칙을 단순·설명가능하게)
    """

    # --- 업종 / 사업 형태 ---
    class Industry(models.TextChoices):
        HEALTHCARE = "healthcare", "헬스케어/의료"
        FINTECH = "fintech", "핀테크/금융"
        ECOMMERCE = "ecommerce", "이커머스/쇼핑"
        EDUTECH = "edutech", "교육"
        SAAS = "saas", "일반 SaaS/IT서비스"
        ETC = "etc", "기타"

    class BusinessType(models.TextChoices):
        B2C = "b2c", "개인 대상(B2C)"
        B2B = "b2b", "기업 대상(B2B)"
        BOTH = "both", "둘 다"

    name = models.CharField("회사명", max_length=200)
    industry = models.CharField("업종", max_length=20, choices=Industry.choices)
    business_type = models.CharField("사업 형태", max_length=10, choices=BusinessType.choices)
    employee_count = models.PositiveIntegerField("직원 수", default=0)

    # --- 취급 데이터 종류 (각 항목이 특정 법령으로 매핑됨) ---
    handles_personal_data = models.BooleanField("개인정보 취급", default=True)          # 개인정보보호법
    handles_sensitive_data = models.BooleanField("민감정보(건강 등) 취급", default=False)  # 개인정보보호법(민감정보)
    handles_location_data = models.BooleanField("위치정보 취급", default=False)          # 위치정보법
    handles_financial_data = models.BooleanField("신용/결제정보 취급", default=False)     # 신용정보법·전자금융거래법
    handles_minor_data = models.BooleanField("만 14세 미만 정보 취급", default=False)     # 개인정보보호법(법정대리인 동의)

    # --- 사업 활동 (각 항목이 특정 법령으로 매핑됨) ---
    does_online_sales = models.BooleanField("온라인 판매", default=False)                # 전자상거래법
    does_marketing = models.BooleanField("광고성 정보 전송(이메일/문자)", default=False)   # 정보통신망법
    overseas_transfer = models.BooleanField("개인정보 국외 이전", default=False)          # 개인정보보호법(국외이전)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_industry_display()})"
