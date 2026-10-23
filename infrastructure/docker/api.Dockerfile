FROM python:3.12-slim
WORKDIR /app
COPY services/analytics-api/requirements.lock .
RUN --mount=type=secret,id=ca_bundle,target=/tmp/ca-bundle \
    if [ -s /tmp/ca-bundle ]; then export PIP_CERT=/tmp/ca-bundle; fi; \
    pip install --no-cache-dir --require-hashes -r requirements.lock
RUN useradd --create-home app
COPY --chown=app:app services/analytics-api/ .
USER app
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && if [ \"$DEMO_MODE\" = \"true\" ]; then python -m app.seed; fi && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
