FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV INPUT_DIR=/app/input
ENV OUTPUT_DIR=/app/output

# Create non-root user
RUN useradd -m appuser
USER appuser

CMD ["python", "main.py"]