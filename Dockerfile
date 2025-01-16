FROM python:3.11-slim
WORKDIR /dockcheck

COPY . /dockcheck

RUN apt-get update && apt-get install -y procps git curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "dockcheck.py"]

