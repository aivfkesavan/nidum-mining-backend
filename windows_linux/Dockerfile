# Use Ubuntu as the base image
FROM ubuntu:latest

# Set working directory
WORKDIR /app

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    curl \
    sudo \
    net-tools \
    ca-certificates \
    gnupg \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment and install dependencies inside it
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copy application files and NetBird CLI tool
COPY app.py requirements.txt netbird ./

# Install Python dependencies in virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# Make app.py and NetBird executable
RUN chmod +x app.py netbird && mv netbird /usr/local/bin/netbird

# Set entrypoint to run Python script and keep the container running
ENTRYPOINT ["/app/venv/bin/python", "/app/app.py"]
