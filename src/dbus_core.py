import asyncio
from abc import ABC
from typing import Optional, Dict, Any

from dbus_next.aio import MessageBus, ProxyInterface
from dbus_next import BusType
from dbus_next.errors import DBusError
from pydantic import ValidationError

from notification_util import AsyncMessageSender
from schemas import LoginSessionShort
from utils.logger.log_manager import get_logger
from utils.dbus_utils import human_read_response


class DBusConnector:
    def __init__(self, bus_type: BusType = BusType.SYSTEM):
        self._bus: Optional[MessageBus] = None
        self._bus_type = bus_type
        self._logger = get_logger('dev')
        self._timeout = 2.0
        self._shutdown_event = asyncio.Event()

    async def dbus_connect(self) -> MessageBus:
        if self._bus is None:
            try:
                self._bus = await MessageBus(bus_type=self._bus_type).connect()
                self._logger.info('DBus connect')
            except DBusError as e:
                self._logger.error(f'DBus Error connection {e}')
                raise
        return self._bus

    def shutdown(self):
        self._logger.info("Shutdown initiated")
        self._shutdown_event.set()
        self._bus.disconnect()

    async def wait_for_shutdown(self):
        await self._shutdown_event.wait()

    async def get_bus_interface(self, bus_name: str, path: str, interface: str) -> ProxyInterface:
        try:
            self._logger.info(f'Get DBus Interface {path} {interface} {bus_name}')
            dbus = await self.dbus_connect()
            session_intro = await dbus.introspect(bus_name=bus_name, path=path, timeout=self._timeout)
            session_object = dbus.get_proxy_object(bus_name=bus_name, path=path, introspection=session_intro)
            interface = session_object.get_interface(interface)
            return interface
        except asyncio.TimeoutError as e:
            self._logger.error(f'Asyncio TimeoutError in get DBus interface {e}')
            raise
        except DBusError as e:
            self._logger.error(f'DBus Error in get Dbus interface {e}')
            raise


class LoginSessionService:
    LOGIN_BUS_NAME = "org.freedesktop.login1"
    LOGIN_MANAGER_PATH = "/org/freedesktop/login1"
    LOGIN_MANAGER_INTERFACE = "org.freedesktop.login1.Manager"
    LOGIN_SESSION_INTERFACE = "org.freedesktop.login1.Session"
    DBUS_PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"

    def __init__(self, dbus_core):
        self._bus = DBusConnector()
        self._logger = get_logger("dev")

    async def get_session_property(self, session_id: str, path: str) -> Dict[str, Any]:
        try:
            self._logger.info(f'Get session {session_id} properties')
            interface = self._bus.get_bus_interface(bus_name=self.LOGIN_BUS_NAME, path=path,
                                                    interface=self.DBUS_PROPERTIES_INTERFACE)
            session_properties = await interface.call_get_all(self._session_interface)
            session_properties_dict = {key: variant.value for key, variant in session_properties.items()}
            return session_properties_dict
        except DBusError as e:
            self._logger.error(f'Dbus Error in get session properties {e}')
            raise

    async def get_manager_interface(self) -> ProxyInterface:
        return await self._bus.get_bus_interface(bus_name=self.LOGIN_BUS_NAME, path=self.LOGIN_MANAGER_PATH,
                                                 interface=self.DBUS_PROPERTIES_INTERFACE)


class NotificationService(ABC):
    async def session_new(self, payload: Dict[str, Any]):
        ...

    async def session_removed(self, _id: str, _path: str):
        ...

    async def all_active_session(self, sessions: list):
        ...


class TelegramNotificationHandler(NotificationService):
    def __init__(self, token: str, user_id: str) -> None:
        self._http_manager = AsyncMessageSender(token, user_id)
        self._logger = get_logger("dev")

    async def session_new(self, payload: Dict[str, Any]):
        try:
            model = LoginSessionShort(**payload)
            response = human_read_response(payload=model.model_dump())
            self._logger.info(f'User {model.name} open session {model.id}')
            await self._http_manager.send_message_to_user(response)
        except ValidationError as e:
            self._logger.error(f'Asyncio ValidationError in on new session {e}')
            raise
        except Exception as e:
            self._logger.error(f'Exception {e}')
            raise

    async def session_removed(self, _id: str, _path: str):
        self._logger.info(_id, _path)
        # await self._http_manager.send_message_to_user()

    async def all_active_session(self, sessions: list):
        self._logger.info(sessions)
        # await self._http_manager.send_message_to_user()


class LogingBusPooler:
    def __init__(self, dbus: DBusConnector, session_service: LogingSessionProperties, notify_service: NotificationService):
        self.dbus = dbus
        self._logger = get_logger('dev')
        self._session = session_service
        self._notify = notify_service

    async def _on_session_new(self, session_id: str, path: str) -> None:
        payload = await self._session.get_session_property(session_id, path)
        await self._notify.session_new(payload)

    async def _on_session_removed(self, session_id: str, path: str) -> None:
        await self._notify.session_removed(session_id, path)

    async def run_monitoring(self):
        try:
            self._logger.info('Start monitoring loging session')
            manager_interface = await self._session.get_manager_interface()
            manager_interface.on_session_new(self._on_session_new)
            manager_interface.on_session_removed(self._on_session_removed)
            sessions = await manager_interface.call_list_sessions()
            self._logger.info(f'List active session {sessions}')
            await self._notify.all_active_session(sessions)
            # await self._http_manager.send_message_to_user(f'Текущие сессии: {sessions}')
            await self.dbus.wait_for_shutdown()
        except DBusError as e:
            self._logger.error(f'DBus error in look session pooler {e}')
            raise
