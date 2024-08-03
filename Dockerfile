FROM python:3.12-slim
WORKDIR /app
COPY main.py ./
COPY templates ./templates
COPY static ./static
RUN pip install pymongo
CMD ["python", "main.py"]
