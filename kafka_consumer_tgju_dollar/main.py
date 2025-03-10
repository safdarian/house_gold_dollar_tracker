from kafka_consumer import KafkaConsumerClient

consumer = KafkaConsumerClient(
            bootstrap_servers="kafka:9092",
            topic="dollar_data",
            group_id="dollar_data_group"
        )
consumer.consume_messages()