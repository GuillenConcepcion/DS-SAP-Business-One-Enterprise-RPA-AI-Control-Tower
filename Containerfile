# Multi-stage Containerfile for Podman / Docker (SAP Business One RPA Suite)
# Lead MLOps Engineer: Guillén Concepción (guillenconcepcion@gmail.com)

FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.10-slim AS runner

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . /app

EXPOSE 8050

ENV PYTHONUNBUFFERED=1 \
    SAP_DB=SBODEMO_ES \
    SAP_HOST=sap-server \
    SAP_PORT=50000

CMD ["python", "run_dashboard.py"]
