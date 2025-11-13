import json
import asyncio

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

from confluent_kafka import Consumer, KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic

from shared.logging.utils import get_logger


logger = get_logger(__name__)


class BaseAdminConsumer(ABC):
    def __init__(
        self,
        brokers: str,
        input_topic: str,
        response_topic: str,
        service_name: str,
        *,
        group_id: Optional[str] = None,
        auto_offset_reset: str = "earliest",
    ):
        self.brokers = brokers
        self.input_topic = input_topic
        self.response_topic = response_topic
        self.service_name = service_name
        self.group_id = group_id or input_topic
        self.auto_offset_reset = auto_offset_reset

        self.consumer: Optional[Consumer] = None
        self.producer: Optional[Producer] = None
        self.running = False

        self._command_handlers: Optional[Dict[str, Callable]] = None

    @abstractmethod
    def get_command_handlers(self) -> Dict[str, Callable]:
        pass

    def _get_handlers(self) -> Dict[str, Callable]:
        if self._command_handlers is None:
            self._command_handlers = self.get_command_handlers()
        return self._command_handlers

    def _ensure_topic_exists(self, topic: str) -> None:
        try:
            admin_client = AdminClient({"bootstrap.servers": self.brokers})

            metadata = admin_client.list_topics(timeout=10)
            existing_topics = set(metadata.topics.keys())

            if topic not in existing_topics:
                logger.info("Creating topic: %s", topic)

                new_topic = NewTopic(
                    topic=topic,
                    num_partitions=1,
                    replication_factor=1,
                )

                fs = admin_client.create_topics([new_topic])

                for topic_name, f in fs.items():
                    try:
                        f.result()
                        logger.info("Topic %s created successfully", topic_name)
                    except Exception as e:
                        logger.error("Failed to create topic %s: %s", topic_name, e)
                        raise
            else:
                logger.debug("Topic %s already exists", topic)

        except Exception as e:
            logger.error("Error ensuring topic exists %s: %s", topic, e)
            raise

    def _initialize_consumer(self) -> None:
        if self.consumer is None:
            try:
                self._ensure_topic_exists(self.input_topic)

                conf = {
                    "bootstrap.servers": self.brokers,
                    "group.id": self.group_id,
                    "auto.offset.reset": self.auto_offset_reset,
                    "log_level": 3,
                }

                self.consumer = Consumer(conf)  # type: ignore
                logger.info("Kafka consumer initialized: %s", self.brokers)
            except Exception as e:
                logger.error("Failed to initialize Kafka consumer: %s", e)
                raise

    def _initialize_producer(self) -> None:
        if self.producer is None:
            try:
                self.producer = Producer({"bootstrap.servers": self.brokers})
                logger.info("Kafka producer initialized: %s", self.brokers)
            except Exception as e:
                logger.error("Failed to initialize Kafka producer: %s", e)
                raise

    async def start(self) -> None:
        try:
            self._initialize_consumer()
            self._initialize_producer()

            if self.consumer is None:
                raise RuntimeError("Kafka consumer is not initialized")

            self.consumer.subscribe([self.input_topic])
            self.running = True

            logger.info("Starting Admin Command Consumer for topic: %s", self.input_topic)
        except Exception as e:
            logger.error("Failed to start consumer: %s", e)
            raise

        while self.running:
            msg = self.consumer.poll(0.1)  # type: ignore

            if msg is None:
                await asyncio.sleep(0.1)
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:  # type: ignore
                    continue
                else:
                    logger.error("Consumer error: %s", msg.error())
                    continue

            try:
                command = json.loads(msg.value().decode("utf-8"))  # type: ignore
                await self.process_command(command)

                self.consumer.commit(msg)  # type: ignore

            except Exception as e:
                logger.error("Error processing message: %s", e)

    async def process_command(self, command: dict) -> None:
        request_id = command.get("request_id")
        payload = command.get("payload") or {}
        file_info = command.get("file")

        if not isinstance(payload, dict):
            logger.error("Invalid payload format for request %s: %s", request_id, type(payload))
            self._send_response(request_id, "error", error="Invalid payload format")
            return

        command_type = payload.get("type")
        data = payload.get("data", {})

        if not isinstance(data, dict):
            logger.error("Invalid data format for request %s: %s", request_id, type(data))
            self._send_response(request_id, "error", error="Invalid data format")
            return

        logger.info("Processing command: %s (request %s)", command_type, request_id)
        if file_info:
            logger.info("File info available: %s", file_info.get("filename", "N/A"))

        handlers = self._get_handlers()

        if command_type not in handlers:
            logger.warning("Unknown command type: %s", command_type)
            self._send_response(
                request_id, "error", error=f"Unknown command type: {command_type}"
            )
            return

        handler = handlers[command_type]

        try:
            result = await handler(data, file_info)
            self._send_response(request_id, "completed", response=result)
        except Exception as e:
            logger.error("Error processing command %s: %s", command_type, e, exc_info=True)
            self._send_response(request_id, "error", error=str(e))

    def _send_response(
        self,
        request_id: Optional[str],
        status: str,
        response: Optional[Any] = None,
        error: Optional[str] = None,
    ) -> None:
        if not request_id:
            logger.warning("Skipping response send because request_id is missing")
            return

        if self.producer is None:
            logger.error("Producer is not initialized, cannot send response")
            return

        payload = {
            "request_id": request_id,
            "service": self.service_name,
            "status": status,
            "response": response,
            "error": error,
        }

        try:
            self.producer.produce(
                self.response_topic,
                json.dumps(payload, default=str).encode("utf-8"),
            )
            self.producer.flush()
            logger.info("Sent admin response for request %s with status %s", request_id, status)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to send admin response: %s", exc)

    def stop(self) -> None:
        self.running = False

        if self.consumer:
            try:
                self.consumer.close()
            except Exception as e:
                logger.warning("Error closing consumer: %s", e)

        if self.producer:
            try:
                self.producer.flush()
            except Exception as e:
                logger.warning("Error flushing producer: %s", e)

