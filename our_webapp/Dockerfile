# Base Python Image
FROM python:3.14-slim

# Prevent Python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Flush print outputs directly
ENV PYTHONUNBUFFERED=1

# Working directory inside container
WORKDIR /app

# Copy requirements first for Docker cache optimization
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose Flask port
EXPOSE 5555

# Flask environment variables
ENV FLASK_APP=run.py

# Start Flask app
CMD ["python", "run.py"]