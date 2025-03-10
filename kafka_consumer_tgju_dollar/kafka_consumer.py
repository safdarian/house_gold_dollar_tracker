from confluent_kafka import Consumer
import json
from datetime import datetime
import subprocess
import clickhouse_connect


with open("credentials.json") as f:
    credentials = json.load(f)
    CLICKHOUSE_HOST = credentials["CLICKHOUSE_HOST"]
    CLICKHOUSE_PORT = credentials["CLICKHOUSE_PORT"]
    CLICKHOUSE_USER = credentials["CLICKHOUSE_USER"]
    CLICKHOUSE_PASSWORD = credentials["CLICKHOUSE_PASSWORD"]
    CLICKHOUSE_DATABASE = credentials["CLICKHOUSE_DATABASE"]


class KafkaConsumerClient:
    def __init__(self, bootstrap_servers='kafka:9092', topic='cleanedData', group_id='cleanedData_group'):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.consumer = Consumer({
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True
        })
        self.consumer.subscribe([self.topic])
        self.running = True
        self.client = clickhouse_connect.get_client(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            username=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD
        )

    def insert_into_clickhouse(self, message):
        insert_query = f"""
            INSERT INTO dollar_data (id, title, price, date, datetime) 
            VALUES (
                {message['id']}, 
                '{message['title']}', 
                {message['price']}, 
                '{message['date']}', 
                '{message['datetime'] if 'datetime' in message else f"{message['date']} 00:00:00"}'
            )
            """
        self.client.command(insert_query)


    def consume_messages(self):
        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Listening for new messages on topic '{self.topic}'...", flush=True)

        try:
            while self.running:
                msg = self.consumer.poll(5.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"⚠️ Error: {msg.error()}", flush=True)
                    continue

                message_value = json.loads(msg.value().decode('utf-8'))
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📩 Received message: {message_value}", flush=True)
                self.insert_into_clickhouse(message_value)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Message inserted into ClickHouse: {message_value}", flush=True)

        except KeyboardInterrupt:
            print("\n🔴 Stopping consumer...", flush=True)
        finally:
            self.close()

    def close(self):
        self.running = False
        self.consumer.close()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Consumer stopped.", flush=True)