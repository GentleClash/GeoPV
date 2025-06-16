FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Create a non-root user and group
RUN addgroup --system --gid 984 app && adduser --system --uid 1000 --gid 984 app

# Install necessary system libraries for dependencies like OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Install Python dependencies
# This is still run as root to install packages system-wide in the container
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's source code
# and set the correct ownership to the new 'app' user
COPY . .
RUN chown -R app:app /app

RUN mkdir -p /app/temp && chown -R app:app /app/temp && chmod 777 /app/temp && mkdir -p /app/results && chown -R app:app /app/results && chmod 777 /app/results
RUN mkdir -p /app/.config/ultralytics && chown -R app:app /app/.config

# Switch to the non-root user
USER app
