from confluent_kafka import Consumer, KafkaError
from core.config import settings
import json
from core.logging import get_logger


logger = get_logger(__name__)


class AdminConsumer:
    def __init__(self):
        self.conf = {
            'bootstrap.servers': settings.MESSAGE_BROKERS,
            'group.id': settings.ADMIN_CONNECTIONS_TOPIC,
            'auto.offset.reset': 'earliest'
        }
        self.consumer = Consumer(self.conf)
        self.running = False
    
    async def start(self):
        self.consumer.subscribe([settings.ADMIN_CONNECTIONS_TOPIC])
        self.running = True
        
        logger.info("Starting Admin Command Consumer")
        
        while self.running:
            msg = self.consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(f"Consumer error: {msg.error()}")
                    continue
            
            try:
                command = json.loads(msg.value().decode('utf-8'))
                await self.process_command(command)
                
                self.consumer.commit(msg)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    async def process_command(self, command: dict):
        command_type = command.get('type')
        data = command.get('data', {})

        logger.info(f"Processing command: {command_type}")
        
    def stop(self):
        self.running = False
        self.consumer.close()


admin_consumer = AdminConsumer()