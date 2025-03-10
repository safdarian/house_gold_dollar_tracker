FROM python:3.9
WORKDIR /app
COPY main.py .
RUN pip install kafka-python confluent-kafka clickhouse-connect
RUN pip install clickhouse-driver
CMD ["python", "main.py"]
