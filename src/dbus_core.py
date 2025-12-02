import asyncio
from typing import Optional

from dbus_next.aio import MessageBus
from dbus_next import BusType
from dbus_next.errors import DBusError
from pydantic import ValidationError

from async_notification_util import AsyncMessageSender, TOKEN, USER_ID
from schemas import LoginSessionShort
from utils.logger.log_manager import get_logger
from utils.dbus_utils import human_read_response


class DBusConnector:
    def __init__(self, bus_type: BusType = BusType.SYSTEM) -> None:
        self._bus: Optional[MessageBus] = None
        self.bus_type = bus_type
        self._logger = get_logger('dev')
        self._timeout = 2.0
        self._shutdown_event = asyncio.Event()

    async def dbus_connect(self) -> MessageBus:
        if self._bus is None:
            try:
                self._bus = await MessageBus(bus_type=self.bus_type).connect()
                self._logger.info('DBus connect')
            except DBusError as e:
                self._logger.error(f'DBusError connection {e}')
                raise
        return self._bus

    def shutdown(self):
        self._logger.info("Shutdown initiated")
        self._shutdown_event.set()

    async def get_bus_interface(self, bus_name, _path, interface):
        try:
            self._logger.info(f'Get DBus Interface {_path} {interface} {bus_name}')
            dbus = await self.dbus_connect()
            session_intro = await dbus.introspect(bus_name=bus_name, path=_path, timeout=self._timeout)
            session_object = dbus.get_proxy_object(bus_name=bus_name, path=_path, introspection=session_intro)
            interface = session_object.get_interface(interface)
            return interface
        except asyncio.TimeoutError as e:
            self._logger.error(f'Asyncio TimeoutError in get D`bus interface {e}')
            raise
        except DBusError as e:
            self._logger.error(f'DBus Error in get D`bus interface {e}')
            raise


class LogingSessionProperties(DBusConnector):
    def __init__(self):
        super().__init__()
        self.loging_bus_name: str = 'org.freedesktop.login1'
        self._properties_interface: str = 'org.freedesktop.DBus.Properties'
        self._session_interface: str = 'org.freedesktop.login1.Session'
        self._http_manager = AsyncMessageSender(TOKEN, USER_ID)

    async def _get_session_property(self, _id, _path):
        try:
            self._logger.info(f'Get session {_id} properties')
            interface = await self.get_bus_interface(bus_name=self.loging_bus_name, _path=_path,
                                                     interface=self._properties_interface)
            session_properties = await interface.call_get_all(self._session_interface)
            session_properties_dict = {key: variant.value for key, variant in session_properties.items()}
            return session_properties_dict
        except DBusError as e:
            self._logger.error(f'Dbus tError in get session properties {e}')
            raise

    async def on_session_new(self, _id, _path):
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

    async def on_session_removed(self, _id, _path):
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
            interface = await self.get_bus_interface(bus_name=self.loging_bus_name, _path=self._loging_path,
                                                     interface=self._loging_manager_interface)
            interface.on_session_new(self.on_session_new)
            interface.on_session_removed(self.on_session_removed)
            sessions = await interface.call_list_sessions()
            self._logger.__init__(f'List active session {sessions}')
            print(sessions)
            # await self._http_manager.send_message_to_user(f'Текущие сессии: {sessions}')
            await self._shutdown_event.wait()
            await self._cleanup_resources()
        except DBusError as e:
            self._logger.error(f'DBus error in look session pooler {e}')
            raise
