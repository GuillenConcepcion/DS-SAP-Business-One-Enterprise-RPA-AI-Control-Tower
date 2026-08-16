# Multi-stage Containerfile/Dockerfile for SAP Business One Enterprise RPA Suite
# Lead MLOps Engineer: Guillén Concepción (guillenconcepcion@gmail.com)

FROM python:3.10-slim AS builder

WORKDIR /app

# Install build tools and python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.10-slim AS runner

WORKDIR /app

# Copy dependencies from builder stage
COPY --from=builder /install /usr/local
COPY . /app

# Expose port for Control Tower Dashboard Web Server
EXPOSE 8050

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    SAP_DB=SBODEMO_ES \
    SAP_HOST=sap-server \
    SAP_PORT=50000

# Default entrypoint runs the interactive RPA suite or web server
CMD ["python", "run_dashboard.py"]
