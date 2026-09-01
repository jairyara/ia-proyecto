FROM node:22-alpine AS frontend-build

WORKDIR /app/dashboard
RUN corepack enable
COPY dashboard/package.json dashboard/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY dashboard/ ./
RUN pnpm build

FROM python:3.13-slim AS api-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt

COPY api/ api/
COPY src/ src/
COPY data/ data/
COPY artifacts/ artifacts/
COPY reports/ reports/
COPY --from=frontend-build /app/dashboard/dist dashboard/dist

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
