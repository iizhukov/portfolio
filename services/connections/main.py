try:
    from confluent_kafka import Consumer, KafkaError
    print(dir(Consumer))
    print("Successfully imported confluent_kafka")
except ImportError as e:
    print(f"Import error: {e}")