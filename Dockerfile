
# Use Python 3.11 on a lightweight Debian Linux image.
FROM python:3.11-slim

# Set /app as the working directory inside the container.
# All following commands execute relative to this directory.
WORKDIR /app

# Prevent Python from generating .pyc bytecode files.
ENV PYTHONDONTWRITEBYTECODE=1

# Disable Python output buffering so logs appear immediately.
ENV PYTHONUNBUFFERED=1

# Install Linux packages required by some Python dependencies.
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the local requirements.txt into /app in the image.
COPY requirements.txt .

# Upgrade pip inside the image.
RUN pip install --no-cache-dir --upgrade pip

# Install all Python packages listed in requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remaining project files into /app.
COPY . .

# Document that the application listens on port 8000.
# EXPOSE does not actually publish the port to your computer.
EXPOSE 8000

# Default command executed when the container starts.
# 0.0.0.0 allows connections through the container network.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
