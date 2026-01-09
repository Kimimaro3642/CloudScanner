FROM python:3.12-slim

WORKDIR /app

# Copy requirements from root (not scanner/)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire scanner folder
COPY scanner/ ./scanner/

# Create reports directory
RUN mkdir -p reports

# Set environment for Azure auth
ENV PYTHONUNBUFFERED=1

# Run scanner
ENTRYPOINT ["python", "-m", "scanner.src.main"]