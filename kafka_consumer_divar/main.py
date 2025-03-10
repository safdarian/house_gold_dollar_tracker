from kafka_consumer import KafkaConsumerClient

consumer = KafkaConsumerClient(
            bootstrap_servers="kafka:9092",
            topic="cleanedData",
            group_id="cleanedData_group"
        )
consumer.consume_messages()