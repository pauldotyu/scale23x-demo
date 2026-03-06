FROM python:3.12-alpine

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip uv && \
    uv pip install --system --no-cache .

RUN addgroup -g 1001 appuser && \
    adduser -D -u 1001 -G appuser appuser

COPY --chown=appuser:appuser parse_schedule.py format_schedule.py ./

RUN mkdir -p /app/output && \
    chown -R appuser:appuser /app/output

USER appuser

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python"]