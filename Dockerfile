# FROM python:3.13.5-slim
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY app.py lexicon.json ./
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
