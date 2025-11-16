import asyncio
import json
from typing import Any, Awaitable, Callable, Optional

from confluent_kafka import Consumer, KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic

from core.config import settings
from core.logging import get_logger


logger = get_logger(__name__)

ResponseHandler = Callable[[dict[str, Any]], Awaitable[None]]


class KafkaManager:
    def __init__(self) -> None:
        self._producer = Producer({"bootstrap.servers": settings.REDPANDA_BROKERS})
        self._consumer = Consumer(
            {
                "bootstrap.servers": settings.REDPANDA_BROKERS,
                "group.id": "admin-service",
                "auto.offset.reset": "earliest",
            }
        )
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._admin_client = AdminClient({"bootstrap.servers": settings.REDPANDA_BROKERS})
        self._ensure_topic(settings.ADMIN_RESPONSE_TOPIC)

    def _ensure_topic(self, topic: str) -> None:
        metadata = self._admin_client.list_topics(timeout=10)
        if topic in metadata.topics:
            return

        new_topic = NewTopic(topic, num_partitions=1, replication_factor=1)
        futures = self._admin_client.create_topics([new_topic])
        future = futures.get(topic)
        if future:
            try:
                future.result()
                logger.info("Created Kafka topic '%s'", topic)
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to create topic '%s': %s", topic, exc)

    async def close(self) -> None:
        self._running = False
        if self._task:
            await self._task
        self._producer.flush()

    async def send(self, topic: str, message: dict[str, Any]) -> None:
        payload = json.dumps(message, default=str).encode("utf-8")

        logger.info("Sending message to topic '%s'", topic)
        self._producer.produce(topic, payload)
        self._producer.flush()

    async def start_response_listener(
        self,
        handler: ResponseHandler,
    ) -> None:
        if self._running:
            return

        self._consumer.subscribe([settings.ADMIN_RESPONSE_TOPIC])
        self._running = True

        async def _consume() -> None:
            try:
                while self._running:
                    msg = self._consumer.poll(1.0)
                    if msg is None:
                        await asyncio.sleep(0.1)
                        continue
                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            continue
                        logger.error("Kafka consumer error: %s", msg.error())
                        continue

                    try:
                        payload = json.loads(msg.value().decode("utf-8"))
                        await handler(payload)
                        self._consumer.commit(msg)
                    except Exception as exc:  # noqa: BLE001
                        logger.error("Failed to handle response message: %s", exc)
            except asyncio.CancelledError:
                logger.info("Kafka response listener cancelled")
            finally:
                self._consumer.close()

        self._task = asyncio.create_task(_consume())

