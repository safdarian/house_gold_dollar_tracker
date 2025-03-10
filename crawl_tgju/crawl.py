from scraper import crawl_live
from kafka_producer import KafkaProducerClient

df_dollar = crawl_live("./configs/config_dollar.json")
df_gold18 = crawl_live("./configs/config_gold18.json")
kafka_producer_dollar = KafkaProducerClient(bootstrap_servers="kafka:9092", topic="dollar_data")
kafka_producer_gold18 = KafkaProducerClient(bootstrap_servers="kafka:9092", topic="gold18_data")

df_dollar["date"] = df_dollar["date"].astype(str)
df_dollar["datetime"] = df_dollar["datetime"].astype(str)

df_gold18["date"] = df_gold18["date"].astype(str)
df_gold18["datetime"] = df_gold18["datetime"].astype(str)

kafka_producer_dollar.send_dataframe(df_dollar)
kafka_producer_gold18.send_dataframe(df_gold18)
