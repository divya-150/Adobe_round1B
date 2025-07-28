# Use official slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY app /app

# Set entry point
ENTRYPOINT ["python", "main.py"]