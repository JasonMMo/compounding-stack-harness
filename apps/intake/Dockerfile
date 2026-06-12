# apps/intake/Dockerfile
# python:3.12-slim 기반 — fastapi + uvicorn + jinja2 + pyyaml
FROM python:3.12-slim

WORKDIR /app

# 의존성 설치 (캐시 레이어 분리)
COPY apps/intake/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 앱 소스 복사
COPY apps/intake/ /app/

# DATA_DIR 기본값 (/app/data — 컨테이너 내부)
# Coolify compose에서 호스트 /data/intake/data → /app/data bind mount
ENV DATA_DIR=/app/data
ENV PYTHONIOENCODING=utf-8

EXPOSE 8080

# --proxy-headers: X-Forwarded-For 신뢰 활성화 (BLOCK-1)
# --forwarded-allow-ips="*": 컨테이너는 published port 없이 Coolify uuid 넷에서
#   Traefik만 접근 가능한 구조이므로 * 허용이 안전하다. 외부 직접 접근 불가.
# --workers 1: 인메모리 rate limit이 단일 프로세스 전제 (FIX-3). 스케일 필요시 Redis로 전환.
# --no-access-log: edit_token이 URL에 포함되므로 PII 로그 출력 금지
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", \
     "--proxy-headers", "--forwarded-allow-ips=*", "--workers", "1", "--no-access-log"]
