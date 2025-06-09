FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Create a non-root user and group
RUN addgroup --system app && adduser --system --group app

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

# Switch to the non-root user
USER app
