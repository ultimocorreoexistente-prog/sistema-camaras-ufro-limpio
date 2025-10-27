FROM python:3.11-slim
WORKDIR /app
RUN pip install flask
COPY simple_app.py .
EXPOSE 8000
CMD ["python", "simple_app.py"]