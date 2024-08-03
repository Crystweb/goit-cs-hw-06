FROM python:3.9-slim

WORKDIR /app

COPY main.py /app
COPY index.html /app
COPY message.html /app
COPY error.html /app
COPY style.css /app
COPY logo.png /app

RUN pip install pymongo

EXPOSE 3000 5000

CMD ["python", "main.py"]
