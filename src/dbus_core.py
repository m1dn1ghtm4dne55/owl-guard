import asyncio
from typing import Optional, Dict, Any

from dbus_next.aio import MessageBus, ProxyInterface
from dbus_next import BusType
from dbus_next.errors import DBusError

from utils.logger.log_manager import get_logger


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
    LOGIN_PATH = "/org/freedesktop/login1"
    LOGIN_MANAGER_INTERFACE = "org.freedesktop.login1.Manager"
    LOGIN_SESSION_INTERFACE = "org.freedesktop.login1.Session"
    DBUS_PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"

    def __init__(self, dbus_core: DBusConnector):
        self._bus = dbus_core
        self._logger = get_logger("dev")

    async def get_session_property(self, session_id: str, path: str) -> Dict[str, Any]:
        try:
            self._logger.info(f'Get session {session_id} properties')
            interface = await self._bus.get_bus_interface(bus_name=self.LOGIN_BUS_NAME, path=path,
                                                    interface=self.DBUS_PROPERTIES_INTERFACE)
            session_properties = await interface.call_get_all(self.LOGIN_SESSION_INTERFACE)
            session_properties_dict = {key: variant.value for key, variant in session_properties.items()}
            return session_properties_dict
        except DBusError as e:
            self._logger.error(f'Dbus Error in get session properties {e}')
            raise

    async def get_manager_interface(self) -> ProxyInterface:
        return await self._bus.get_bus_interface(bus_name=self.LOGIN_BUS_NAME, path=self.LOGIN_PATH,
                                                 interface=self.LOGIN_MANAGER_INTERFACE)


