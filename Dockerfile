# Use an official Python 3.12 slim image as a parent image.
FROM python:3.12-slim

# Set environment variable to disable Python buffering (useful for logs).
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install any system dependencies required by the project.
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container.
WORKDIR /app

# Upgrade pip.
RUN pip install --upgrade pip

# Copy the requirements file into the container.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install -r requirements.txt

# Copy the rest of the project code into the container.
COPY . .

# Define the default command to run the pipeline.
CMD ["python", "src/main.py"]
