import asyncio
import grpc

from dataclasses import dataclass
from typing import Optional

from shared.logging.utils import get_logger

from generated.modules import modules_pb2, modules_pb2_grpc


logger = get_logger(__name__)


@dataclass(slots=True)
class RegistrationParams:
    service_name: str
    version: str
    admin_topic: str


class ModulesClient:
    def __init__(
        self,
        target: str,
        registration: RegistrationParams,
        *,
        heartbeat_interval: Optional[int] = None,
    ) -> None:
        self._target = target
        self._registration = registration
        self._requested_interval = heartbeat_interval

        self._channel: Optional[grpc.aio.Channel] = None
        self._stub: Optional[modules_pb2_grpc.ModulesServiceStub] = None

        self._instance_id: Optional[str] = None
        self._ttl_seconds: Optional[int] = None
        self._heartbeat_interval: Optional[float] = None
        self._last_heartbeat_ok: bool = False

        self._heartbeat_task: Optional[asyncio.Task[None]] = None
        self._stop_event = asyncio.Event()

    @property
    def instance_id(self) -> Optional[str]:
        return self._instance_id

    @property
    def ttl_seconds(self) -> Optional[int]:
        return self._ttl_seconds

    @property
    def is_connected(self) -> bool:
        return self._channel is not None and self._instance_id is not None

    @property
    def is_healthy(self) -> bool:
        return self.is_connected and self._last_heartbeat_ok

    async def start(self) -> None:
        if self._channel:
            return

        logger.info("Connecting to modules service at %s", self._target)
        self._channel = grpc.aio.insecure_channel(self._target)
        self._stub = modules_pb2_grpc.ModulesServiceStub(self._channel)

        await self._register()
        self._stop_event.clear()
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def stop(self) -> None:
        self._stop_event.set()

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            finally:
                self._heartbeat_task = None

        if self._stub and self._instance_id:
            try:
                await self._stub.Deregister(
                    modules_pb2.DeregisterRequest(instance_id=self._instance_id)
                )
                logger.info("Deregistered from modules service")
            except grpc.aio.AioRpcError as exc:
                logger.warning("Deregister call failed: %s", exc.details())

        if self._channel:
            await self._channel.close()
            self._channel = None
            self._stub = None
            self._instance_id = None
            self._ttl_seconds = None

    async def _register(self) -> None:
        assert self._stub is not None

        request = modules_pb2.RegisterRequest(
            service_name=self._registration.service_name,
            version=self._registration.version,
            admin_topic=self._registration.admin_topic,
        )

        try:
            response = await self._stub.Register(request)
        except grpc.aio.AioRpcError as exc:
            logger.error("Failed to register with modules: %s", exc.details())
            raise

        self._instance_id = response.instance_id
        self._ttl_seconds = response.ttl_seconds or 30
        self._last_heartbeat_ok = True

        base_interval = max(self._ttl_seconds // 2, 1)
        self._heartbeat_interval = (
            float(self._requested_interval)
            if self._requested_interval
            else float(base_interval)
        )

        logger.info(
            "Registered service '%s' (instance=%s, ttl=%ss)",
            self._registration.service_name,
            self._instance_id,
            self._ttl_seconds,
        )

    async def _heartbeat_loop(self) -> None:
        assert self._stub is not None
        assert self._instance_id is not None
        interval = self._heartbeat_interval or 10.0

        while not self._stop_event.is_set():
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=interval)
                if self._stop_event.is_set():
                    break
            except asyncio.TimeoutError:
                pass

            try:
                response = await self._stub.Heartbeat(
                    modules_pb2.HeartbeatRequest(instance_id=self._instance_id)
                )
                if response.ttl_seconds:
                    self._ttl_seconds = response.ttl_seconds
                    base_interval = max(self._ttl_seconds // 2, 1)
                    if not self._requested_interval:
                        self._heartbeat_interval = float(base_interval)
                self._last_heartbeat_ok = True
                logger.debug("Heartbeat acknowledged for instance %s", self._instance_id)
            except grpc.aio.AioRpcError as exc:
                logger.warning(
                    "Heartbeat failed for instance %s: %s",
                    self._instance_id,
                    exc.details(),
                )
                self._last_heartbeat_ok = False
                await asyncio.sleep(5)


