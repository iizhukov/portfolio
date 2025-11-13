import os
import json
import signal
import asyncio

from typing import Any
from confluent_kafka import Consumer, KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic

from core.config import settings
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
        self.producer = Producer({'bootstrap.servers': settings.MESSAGE_BROKERS})
    
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
                
                self.consumer = Consumer(self.conf) # type: ignore
                logger.info(f"Kafka consumer initialized: {settings.MESSAGE_BROKERS}")
            except Exception as e:
                logger.error(f"Failed to initialize Kafka consumer: {e}")
                raise
    
    async def start(self):
        try:
            self._initialize_consumer()

            if self.consumer is None:
                raise Exception("Kafka consumer is not initialized")

            self.consumer.subscribe([settings.ADMIN_CONNECTIONS_TOPIC])
            self.running = True
            
            logger.info("Starting Admin Command Consumer")
        except Exception as e:
            logger.error(f"Failed to start consumer: {e}")
            return
        
        while self.running:
            msg = self.consumer.poll(0.1)

            if msg is None:
                await asyncio.sleep(0.1)
                continue
                
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF: # type: ignore
                    continue
                else:
                    logger.error(f"Consumer error: {msg.error()}")
                    continue

            try:
                command = json.loads(msg.value().decode('utf-8')) # type: ignore
                await self.process_command(command)
                
                self.consumer.commit(msg)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    async def process_command(self, command: dict):
        request_id = command.get('request_id')
        payload = command.get('payload') or {}
        file_info = command.get('file')
        if not isinstance(payload, dict):
            logger.error("Invalid payload format for request %s: %s", request_id, type(payload))
            self._send_response(request_id, 'error', error="Invalid payload format")
            return
        command_type = payload.get('type')
        data = payload.get('data', {})
        if not isinstance(data, dict):
            logger.error("Invalid data format for request %s: %s", request_id, type(data))
            self._send_response(request_id, 'error', error="Invalid data format")
            return

        logger.info(f"Processing command: {command_type} (request {request_id})")
        if file_info:
            logger.info(f"File info available: {file_info.get('filename', 'N/A')}")
        
        try:
            result = None

            if command_type == 'create_connection':
                result = await self._create_connection(data)
            elif command_type == 'update_connection':
                result = await self._update_connection(data)
            elif command_type == 'delete_connection':
                result = await self._delete_connection(data)
            elif command_type == 'update_status':
                result = await self._update_status(data)
            elif command_type == 'update_working':
                result = await self._update_working(data)
            elif command_type == 'update_image':
                result = await self._update_image(data, file_info)
            elif command_type == 'shutdown_service':
                result = await self._shutdown_service(data)
            else:
                logger.warning(f"Unknown command type: {command_type}")
                self._send_response(request_id, 'error', error=f"Unknown command type: {command_type}")
                return

            self._send_response(request_id, 'completed', response=result)
        except Exception as e:
            logger.error(f"Error processing command {command_type}: {e}")
            self._send_response(request_id, 'error', error=str(e))
    
    async def _create_connection(self, data: dict):
        from core.database import db_manager
        from schemas.connection import ConnectionCreateSchema
        from services.connection_service import ConnectionService
        
        async for db in db_manager.get_session():
            service = ConnectionService(db)
            connection_data = ConnectionCreateSchema(**data)
            connection = await service.create_connection(connection_data)
            logger.info(f"Created connection: {connection.id} - {connection.label}")
            return connection.to_dict()
    
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
                result = connection.to_dict()
                return result
            else:
                logger.warning(f"Connection {connection_id} not found for update")
                return None
    
    async def _delete_connection(self, data: dict):
        from core.database import db_manager
        from services.connection_service import ConnectionService
        
        connection_id = data.pop('id')
        async for db in db_manager.get_session():
            service = ConnectionService(db)
            success = await service.delete_connection(connection_id)

            if success:
                logger.info(f"Deleted connection: {connection_id}")
                return {"deleted": True}
            else:
                logger.warning(f"Connection {connection_id} not found for deletion")
                return {"deleted": False}
    
    async def _update_status(self, data: dict):
        from core.database import db_manager
        from services.status_service import StatusService
        
        async for db in db_manager.get_session():
            service = StatusService(db)
            status = await service.update_status(data.get('status', 'active'))
            logger.info(f"Updated status: {status.status}")
            return {"status": status.status}
    
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
            return {
                "working_on": working.working_on,
                "percentage": working.percentage
            }
    
    async def _update_image(self, data: dict, file_info: dict | None = None):
        from core.database import db_manager
        from schemas.image import ImageUpdateSchema
        from services.image_service import ImageService
        
        if file_info:
            update_data = {
                "filename": file_info.get("filename", ""),
                "content_type": file_info.get("content_type", ""),
                "url": file_info.get("url", "")
            }
        else:
            update_data = data
        
        async for db in db_manager.get_session():
            service = ImageService(db)
            image_data = ImageUpdateSchema(**update_data)
            image = await service.update_image(image_data)
            
            if image:
                logger.info(f"Updated image: {image.id} - {image.filename}")
                result = image.to_dict()
                return result
            else:
                logger.warning("Image not found for update. Image must exist first.")
                return None
    
    async def _shutdown_service(self, data: dict):
        import asyncio
        
        reason = data.get('reason', 'No reason provided')
        logger.warning(f"Shutdown command received via Kafka. Reason: {reason}")

        await asyncio.sleep(0.5)
        
        logger.info("Initiating graceful shutdown...")
        os.kill(os.getpid(), signal.SIGTERM)
        return {"shutdown": True, "reason": reason}

    def stop(self):
        self.running = False

        if self.consumer:
            try:
                self.consumer.close()
            except Exception as e:
                logger.warning(f"Error closing consumer: {e}")

    def _send_response(
        self,
        request_id: str | None,
        status: str,
        response: dict | None = None,
        error: str | None = None,
    ) -> None:
        if not request_id:
            logger.warning("Skipping response send because request_id is missing")
            return

        payload = {
            "request_id": request_id,
            "service": "connections",
            "status": status,
            "response": response,
            "error": error,
        }

        try:
            self.producer.produce(
                settings.ADMIN_RESPONSE_TOPIC,
                json.dumps(payload, default=str).encode('utf-8'),
            )
            self.producer.flush()
            logger.info("Sent admin response for request %s with status %s", request_id, status)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Failed to send admin response: {exc}")


admin_consumer = AdminConsumer()
