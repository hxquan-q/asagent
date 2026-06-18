# Sandbox image for the Docker sandbox backend (skill script execution).
# Read-only fs + --network=none at run time; common data libs preinstalled.
FROM python:3.11-slim
RUN pip install --no-cache-dir pandas numpy openpyxl requests httpx pyyaml
RUN mkdir -p /work && chown -R 65534:65534 /work
USER 65534
WORKDIR /work
