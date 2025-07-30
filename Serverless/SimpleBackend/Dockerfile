# 🚀 MINIMAL DOCKERFILE for Simple Backend
FROM python:3.12-slim

# Essential settings only
ENV PYTHONUNBUFFERED=1

# Work directory
WORKDIR /app

# Install minimal dependencies
RUN pip install --no-cache-dir runpod

# Copy handler
COPY handler.py .

# Expose port (RunPod standard)
EXPOSE 8000

# Start handler
CMD ["python", "-u", "handler.py"] 