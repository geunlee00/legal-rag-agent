# Django(백엔드)를 실행하는 컨테이너 레시피

# 1. 베이스 이미지: 파이썬 3.11 (가벼운 slim 버전)
FROM python:3.11-slim

# 2. 파이썬 로그가 바로 보이게 + .pyc 파일 안 만들게
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. 컨테이너 안의 작업 폴더
WORKDIR /app

# 4. 라이브러리 목록을 먼저 복사·설치
#    (코드보다 먼저 하는 이유: requirements가 안 바뀌면 이 단계는 캐시 재사용 → 빌드 빠름)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 나머지 프로젝트 코드 전체 복사
COPY . .

# 6. 기본 실행 명령: gunicorn으로 Django를 8000 포트에서 구동
#    (migrate·collectstatic은 이후 docker-compose에서 실행 전에 돌린다)
CMD ["gunicorn", "solo_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
