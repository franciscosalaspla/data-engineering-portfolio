FROM python:3.11-slim

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY 18-pipeline-dockerizado-agent-loop/requirements.txt ./18-pipeline-dockerizado-agent-loop/requirements.txt

RUN pip install --no-cache-dir -r ./18-pipeline-dockerizado-agent-loop/requirements.txt

COPY 17-dbt-professional-ecommerce ./17-dbt-professional-ecommerce
COPY 18-pipeline-dockerizado-agent-loop ./18-pipeline-dockerizado-agent-loop

WORKDIR /workspace/18-pipeline-dockerizado-agent-loop

RUN mkdir -p output logs

CMD ["python", "app/run_pipeline.py"]
