import asyncio
from typing import Optional, Dict, Any

from dbus_next.aio import MessageBus, ProxyInterface
from dbus_next import BusType
from dbus_next.errors import DBusError
from pydantic import ValidationError

from constants import TOKEN, USER_ID
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


class LogingSessionProperties:
    LOGIN_BUS_NAME = "org.freedesktop.login1"
    LOGIN_MANAGER_PATH = "/org/freedesktop/login1"
    LOGIN_MANAGER_INTERFACE = "org.freedesktop.login1.Manager"
    LOGIN_SESSION_INTERFACE = "org.freedesktop.login1.Session"
    DBUS_PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"

    def __init__(self):
        self._loging_bus_name: str = 'org.freedesktop.login1'
        self._properties_interface: str = 'org.freedesktop.DBus.Properties'
        self._session_interface: str = 'org.freedesktop.login1.Session'
        self.bus = DBusConnector()
        self._logger = get_logger("dev")

    async def _get_session_property(self, session_id: str, path: str) -> Dict[str, Any]:
        try:
            self._logger.info(f'Get session {session_id} properties')
            interface = self.bus.get_bus_interface(bus_name=self.LOGIN_BUS_NAME, path=path, interface=self.DBUS_PROPERTIES_INTERFACE)
            session_properties = await interface.call_get_all(self._session_interface)
            session_properties_dict = {key: variant.value for key, variant in session_properties.items()}
            return session_properties_dict
        except DBusError as e:
            self._logger.error(f'Dbus Error in get session properties {e}')
            raise

    async def get_manager_interface_dbus(self):
        return await self.bus.get_bus_interface(bus_name=self.LOGIN_BUS_NAME, path=self.LOGIN_MANAGER_PATH,
                                                interface=self.DBUS_PROPERTIES_INTERFACE)

    async def on_session_new(self, _id: str, _path: str):
        payload = await self._get_session_property(_id, _path)
        try:
            self._logger.info(f'Send info about new login session {_id} to webhook')
            response = human_read_response(payload=LoginSessionShort(**payload).model_dump())
            await self._http_manager.send_message_to_user(response)
        except ValidationError as e:
            self._logger.error(f'Asyncio ValidationError in on new session {e}')
            raise
        except Exception as e:
            self._logger.error(f'Exception {e}')
            raise

    async def on_session_removed(self, _id: str, _path: str):
        print(_id, _path)
        # await self._http_manager.send_message_to_user()


class LogingBusPooler(LogingSessionProperties):
    def __init__(self):
        self._loging_path = '/org/freedesktop/login1'
        self._loging_manager_interface = 'org.freedesktop.login1.Manager'
        super().__init__()

    async def _cleanup_resources(self):
        try:
            if self._bus:
                self._bus.disconnect()
                self._logger.info('DBus connection disconnected')
        except Exception as e:
            self._logger.error(f'Error shutdown: {e}')
        finally:
            self._logger.info('Shutdown completed')

    async def look_sessions(self):
        try:
            self._logger.info('Start pooling loging session')
            interface = await self.get_bus_interface(bus_name=self._loging_bus_name, _path=self._loging_path,
                                                     interface=self._loging_manager_interface)
            interface.on_session_new(self.on_session_new)
            interface.on_session_removed(self.on_session_removed)
            sessions = await interface.call_list_sessions()
            self._logger.info(f'List active session {sessions}')
            print(sessions)
            # await self._http_manager.send_message_to_user(f'Текущие сессии: {sessions}')
            await self._shutdown_event.wait()
            await self._cleanup_resources()
        except DBusError as e:
            self._logger.error(f'DBus error in look session pooler {e}')
            raise
