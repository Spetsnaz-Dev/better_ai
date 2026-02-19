# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /build
COPY api/requirements.txt .

# Install dependencies to the local user directory
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Final minimal image
FROM python:3.11-slim

WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Ensure the local bin is on PATH so Python finds the installed packages
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Copy the application code
COPY api/ .

# Expose backend port
EXPOSE 5000

# Healthcheck to verify standard API operation without relying on external curl
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Start the Flask app
CMD ["python", "run.py"]
