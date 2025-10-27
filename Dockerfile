FROM python:3.11-slim
WORKDIR /app
RUN pip install flask
COPY . .
EXPOSE $PORT
CMD ["sh", "-c", "python simple_app.py"]