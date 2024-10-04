# Use Python 3.10-slim
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy current directory to container
COPY . /app

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Expose port 8000
EXPOSE 8000

# Run Flask using Gunicorn on port 8000
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "app:app"]