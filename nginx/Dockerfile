# nginx: React를 빌드해서 서빙 + API 프록시

# ── 1단계: React 빌드 (node 환경) ──
FROM node:22-alpine AS build
WORKDIR /app
# 라이브러리 먼저 설치 (캐시 활용)
COPY frontend/package*.json ./
RUN npm install
# 프론트 코드 복사 후 빌드 → /app/dist 에 정적파일 생성
COPY frontend/ ./
RUN npm run build

# ── 2단계: nginx로 서빙 (가벼운 이미지) ──
FROM nginx:alpine
# 1단계에서 만든 빌드 결과물만 복사 (node/node_modules는 안 가져옴)
COPY --from=build /app/dist /usr/share/nginx/html
# 우리가 만든 nginx 설정으로 교체
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
