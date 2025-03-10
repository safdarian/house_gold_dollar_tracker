
from confluent_kafka import Producer
import json
from datetime import datetime

class KafkaProducerClient:
    def __init__(self, bootstrap_servers='kafka:9092', topic='cleanedData'):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = Producer({
            'bootstrap.servers': self.bootstrap_servers,
            'acks': 'all',
            'linger.ms': 100,
        })

    def delivery_report(self, err, msg):
        if err is not None:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Message delivery failed: {err}", flush=True)
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Message delivered to {msg.topic()} [{msg.partition()}]", flush=True)

    def send_dataframe(self, df):
        if df.empty:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ DataFrame is empty. Nothing to send.", flush=True)
            return

        records = df.to_dict(orient="records")

        for record in records:
            self.producer.produce(
                self.topic,
                json.dumps(record).encode('utf-8'),
                callback=self.delivery_report
            )

        self.producer.flush()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Sent {len(records)} records to Kafka topic '{self.topic}'", flush=True)
