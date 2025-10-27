FROM python:3.11-slim
WORKDIR /app
RUN pip install flask
COPY minimal.py .
EXPOSE 8000
CMD ["python", "minimal.py"]