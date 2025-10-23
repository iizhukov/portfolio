from confluent_kafka import Consumer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
from core.config import settings
import json
from core.logging import get_logger


logger = get_logger(__name__)


class AdminConsumer:
    def __init__(self):
        self.conf = {
            'bootstrap.servers': settings.MESSAGE_BROKERS,
            'group.id': settings.ADMIN_CONNECTIONS_TOPIC,
            'auto.offset.reset': 'earliest',
            'log_level': 3,
        }
        self.consumer = None
        self.running = False
    
    def _ensure_topic_exists(self):
        try:
            admin_client = AdminClient({'bootstrap.servers': settings.MESSAGE_BROKERS})
            
            metadata = admin_client.list_topics(timeout=10)
            existing_topics = set(metadata.topics.keys())
            
            if settings.ADMIN_CONNECTIONS_TOPIC not in existing_topics:
                logger.info(f"Creating topic: {settings.ADMIN_CONNECTIONS_TOPIC}")
                
                new_topic = NewTopic(
                    topic=settings.ADMIN_CONNECTIONS_TOPIC,
                    num_partitions=1,
                    replication_factor=1
                )
                
                fs = admin_client.create_topics([new_topic])
                
                for topic, f in fs.items():
                    try:
                        f.result()
                        logger.info(f"Topic {topic} created successfully")
                    except Exception as e:
                        logger.error(f"Failed to create topic {topic}: {e}")
                        raise
            else:
                logger.info(f"Topic {settings.ADMIN_CONNECTIONS_TOPIC} already exists")
                
        except Exception as e:
            logger.error(f"Error ensuring topic exists: {e}")
            raise
    
    def _initialize_consumer(self):
        if self.consumer is None:
            try:
                self._ensure_topic_exists()
                
                self.consumer = Consumer(self.conf)
                logger.info(f"Kafka consumer initialized: {settings.MESSAGE_BROKERS}")
            except Exception as e:
                logger.error(f"Failed to initialize Kafka consumer: {e}")
                raise
    
    async def start(self):
        try:
            self._initialize_consumer()

            self.consumer.subscribe([settings.ADMIN_CONNECTIONS_TOPIC])
            self.running = True
            
            logger.info("Starting Admin Command Consumer")
        except Exception as e:
            logger.error(f"Failed to start consumer: {e}")
            return
        
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
        
        try:
            if command_type == 'create_connection':
                await self._create_connection(data)
            elif command_type == 'update_connection':
                await self._update_connection(data)
            elif command_type == 'delete_connection':
                await self._delete_connection(data)
            elif command_type == 'update_status':
                await self._update_status(data)
            elif command_type == 'update_working':
                await self._update_working(data)
            else:
                logger.warning(f"Unknown command type: {command_type}")
        except Exception as e:
            logger.error(f"Error processing command {command_type}: {e}")
    
    async def _create_connection(self, data: dict):
        from core.database import db_manager
        from schemas.connection import ConnectionCreateSchema
        from services.connection_service import ConnectionService
        
        async for db in db_manager.get_session():
            service = ConnectionService(db)
            connection_data = ConnectionCreateSchema(**data)
            connection = await service.create_connection(connection_data)
            logger.info(f"Created connection: {connection.id} - {connection.label}")
    
    async def _update_connection(self, data: dict):
        from core.database import db_manager
        from schemas.connection import ConnectionUpdateSchema
        from services.connection_service import ConnectionService
        
        connection_id = data.pop('id')
        async for db in db_manager.get_session():
            service = ConnectionService(db)
            connection_data = ConnectionUpdateSchema(**data)
            connection = await service.update_connection(connection_id, connection_data)

            if connection:
                logger.info(f"Updated connection: {connection.id} - {connection.label}")
            else:
                logger.warning(f"Connection {connection_id} not found for update")
    
    async def _delete_connection(self, data: dict):
        from core.database import db_manager
        from services.connection_service import ConnectionService
        
        connection_id = data.pop('id')
        async for db in db_manager.get_session():
            service = ConnectionService(db)
            success = await service.delete_connection(connection_id)

            if success:
                logger.info(f"Deleted connection: {connection_id}")
            else:
                logger.warning(f"Connection {connection_id} not found for deletion")
    
    async def _update_status(self, data: dict):
        from core.database import db_manager
        from services.status_service import StatusService
        
        async for db in db_manager.get_session():
            service = StatusService(db)
            status = await service.update_status(data.get('status', 'active'))
            logger.info(f"Updated status: {status.status}")
    
    async def _update_working(self, data: dict):
        from core.database import db_manager
        from services.working_service import WorkingService
        
        async for db in db_manager.get_session():
            service = WorkingService(db)
            working = await service.update_working_status(
                data.get('working_on', ''),
                data.get('percentage', 0)
            )
            logger.info(f"Updated working: {working.working_on} - {working.percentage}%")

    def stop(self):
        self.running = False

        if self.consumer:
            try:
                self.consumer.close()
            except Exception as e:
                logger.warning(f"Error closing consumer: {e}")


admin_consumer = AdminConsumer()
