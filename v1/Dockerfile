# Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and manifest
COPY . .

# Expose port
EXPOSE 8000

# Point Uvicorn at app.py's FastAPI instance
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
