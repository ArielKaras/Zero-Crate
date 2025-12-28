# Stage 1: Builder
# We use a larger image to build dependencies, then discard it.
FROM python:3.13-slim as builder

WORKDIR /app

# Install build tools (GCC) needed for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runner
# This is the final, minimal image.
FROM python:3.13-slim as runner

WORKDIR /app

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code (Allowed by .dockerignore)
COPY . .

# Security: Ensure we don't carry any accidental root ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (Documentation only)
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
