#!/usr/bin/env bash

# 1. Get total CPU cores
TOTAL_CPUS=$(nproc)  # e.g., 8
EIGHTY_PCT_CPUS=$(awk -v c=$TOTAL_CPUS 'BEGIN { printf "%.2f", c*0.80 }')  # 6.4

# 2. Get total system memory in MB (or in KiB, then convert)
TOTAL_MEM_KB=$(awk '/MemTotal/ { print $2 }' /proc/meminfo)
TOTAL_MEM_MB=$((TOTAL_MEM_KB/1024))    # e.g., 16000 for 16GB
EIGHTY_PCT_MB=$((TOTAL_MEM_MB*80/100)) # e.g., 12800 for 12.8GB

# 3. Generate a Docker Compose file or use env substitution
cat <<EOF > docker-compose.generated.yml
version: "3.8"

services:
  exo_1:
    build:
      context: .
    environment:
      - PYTHONUNBUFFERED=1
    ports:
      - "52415:52415"
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
    command: ["exo", "--inference-engine", "mlx"]

    deploy:
      resources:
        limits:
          cpus: "${EIGHTY_PCT_CPUS}"
          memory: "${EIGHTY_PCT_MB}M"
        reservations:
          cpus: "${EIGHTY_PCT_CPUS}"
          memory: "${EIGHTY_PCT_MB}M"

networks:
  exo_network:
    driver: bridge
EOF

# 4. Deploy using the generated file:
docker compose -f docker-compose.generated.yml up -d
