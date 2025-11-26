FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY config.py .
COPY db_setup.py .
COPY start.sh .
COPY models ./models
COPY routes ./routes
COPY templates ./templates
COPY static ./static
RUN chmod +x start.sh && mkdir -p uploads logs
CMD ["./start.sh"]