from asyncio import Future
from os import getenv

from dbus_next.aio import MessageBus
from dbus_next import BusType
from dotenv import load_dotenv

from async_notification_util import AsyncMessageSender

load_dotenv()
TOKEN = getenv('TOKEN')
USER_ID = getenv('USER_ID')

http_manager = AsyncMessageSender(TOKEN, USER_ID)


class DBusConnector:
    def __init__(self, bus_type: BusType = BusType.SYSTEM) -> None:
        self._bus: MessageBus | None = None
        self.bus_type = bus_type

    async def dbus_connect(self) -> MessageBus:
        if self._bus is None:
            self._bus = await MessageBus(bus_type=self.bus_type).connect()
        return self._bus

    async def get_bus_interface(self, bus_name, _path, interface):
        dbus = await self.dbus_connect()
        session_intro = await dbus.introspect(bus_name=bus_name, path=_path, timeout=2.0)
        session_object = dbus.get_proxy_object(bus_name=bus_name, path=_path, introspection=session_intro)
        interface = session_object.get_interface(interface)
        return interface


class LogingSessionProperties(DBusConnector):
    def __init__(self):
        super().__init__()
        self.loging_bus_name: str = 'org.freedesktop.login1'
        self._properties_interface: str = 'org.freedesktop.DBus.Properties'
        self._session_interface: str = 'org.freedesktop.login1.Session'

    async def on_session_new(self, _id, _path):
        interface = await self.get_bus_interface(bus_name=self.loging_bus_name, _path=_path,
                                                 interface=self._properties_interface)
        session_properties = await interface.call_get_all(self._session_interface)
        for key, value in session_properties.items():
            print(key, value, sep=' | ')
        # await http_manager.send_message_to_user(f'Новая сессия SSH {_id}\n{_path}\nСвойства сессии: {session_properties}')

    async def on_session_removed(self, _id, _path):
        print(_id, _path)
        # await http_manager.send_message_to_user()


class LogingBusPooler(LogingSessionProperties):
    def __init__(self):
        self._loging_path = '/org/freedesktop/login1'
        self._loging_manager_interface = 'org.freedesktop.login1.Manager'
        super().__init__()

    async def look_sessions(self):
        interface = await self.get_bus_interface(bus_name=self.loging_bus_name, _path=self._loging_path,
                                                 interface=self._loging_manager_interface)
        interface.on_session_new(self.on_session_new)
        interface.on_session_removed(self.on_session_removed)
        sessions = await interface.call_list_sessions()
        print(sessions)
        # await http_manager.send_message_to_user(f'Текущие сессии: {sessions}')
        await Future()
