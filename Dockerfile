# Base image: Python 3.11 with Alpine
FROM python:3.11-alpine

# Environment Variables:
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Security: Create a non-root user
RUN adduser -D appuser

# Define the working directory
WORKDIR /app

# Install system dependencies, build tools, and timezone data
RUN apk add --no-cache \
    tzdata \
    gcc \
    musl-dev \
    libffi-dev \
    build-base \
    && cp /usr/share/zoneinfo/Asia/Jakarta /etc/localtime \
    && echo "Asia/Jakarta" > /etc/timezone \
    && rm -rf /var/cache/apk/*

# Stage 1: Copy dependencies list and install Python packages
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Copy the application code to the working directory
COPY . .

# Change ownership of the application files to the non-root user.
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Default command to run the application
CMD ["python", "main.py"]
