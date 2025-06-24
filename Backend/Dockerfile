FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Create a non-root user and group
RUN addgroup --system --gid 984 app && adduser --system --uid 1000 --gid 984 app

# Install necessary system libraries for dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R app:app /app \
    && mkdir -p /app/temp /app/results /app/.config/ultralytics \
    && chown -R app:app /app/temp /app/results /app/.config \
    && chmod 775 /app/temp /app/results


# Switch to the non-root user
USER app
