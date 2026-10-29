FROM python:3.13-slim

WORKDIR /app

# Install system dependencies (ffmpeg for audio conversion, curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy backend source code and samples
COPY backend /app/backend
COPY samples /app/samples

ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

EXPOSE 3038

CMD ["python3", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "3038"]

