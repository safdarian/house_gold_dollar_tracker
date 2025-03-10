from kafka_consumer import KafkaConsumerClient

consumer = KafkaConsumerClient(
            bootstrap_servers="kafka:9092",
            topic="gold18_data",
            group_id="gold18_data_group"
        )
consumer.consume_messages()