FROM python:3.11-slim
WORKDIR /dockcheck

COPY . /dockcheck

RUN apt-get update && apt-get install -y procps git curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD pgrep -fl dockcheck || exit 1

CMD ["python", "dockcheck.py"]

