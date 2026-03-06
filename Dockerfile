# Dockerfile
# ---- base image with wheels available ----
FROM python:3.11-slim

WORKDIR /app

# ---- dependencies ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- app code ----
COPY src/ ./src/
COPY app.py lexicons.json ./

# ---- expose port & health check ----
ENV PORT=7860
HEALTHCHECK CMD curl -f http://localhost:${PORT}/_stcore/health || exit 1

# ---- launch ----
CMD ["streamlit", "run", "app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
