FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY 17-dbt-professional-ecommerce ./17-dbt-professional-ecommerce
COPY 18-pipeline-dockerizado-agent-loop ./18-pipeline-dockerizado-agent-loop

WORKDIR /workspace/18-pipeline-dockerizado-agent-loop

RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p output logs

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python app/health_check.py || exit 1

CMD ["python", "app/run_pipeline.py"]
