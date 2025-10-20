# Build stage
FROM node:18-alpine AS build

WORKDIR /app

# 의존성 설치
COPY package.json ./
RUN npm install -g pnpm && pnpm install

# 소스 코드 복사 및 빌드
COPY . .
RUN pnpm build

# Production stage
FROM nginx:alpine

# Nginx 설정 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 빌드된 파일 복사
COPY --from=build /app/dist /usr/share/nginx/html

# 포트 노출
EXPOSE 80

# 실행
CMD ["nginx", "-g", "daemon off;"]

