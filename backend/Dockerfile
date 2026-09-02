FROM python:3.12-slim
WORKDIR /app
ENV PYTHONPATH=/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY scripts ./scripts
RUN mkdir -p /app/data
EXPOSE 8000
CMD ["sh", "-c", "python -m scripts.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000"]