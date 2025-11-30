import asyncio
from os import getenv

from dbus_next.aio import MessageBus
from dbus_next import BusType
from dotenv import load_dotenv

from async_notification_util import AsyncMessageSender

load_dotenv()
TOKEN = getenv('TOKEN')
USER_ID = getenv('USER_ID')

http_manager = AsyncMessageSender(TOKEN, USER_ID)
loop = asyncio.get_event_loop()

async def look_sessions():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    introspection = await bus.introspect('org.freedesktop.login1', path='/org/freedesktop/login1',timeout=2.0)
    obj = bus.get_proxy_object('org.freedesktop.login1', '/org/freedesktop/login1', introspection)
    manager = obj.get_interface('org.freedesktop.login1.Manager')
    async def on_session_new(_id, _path):
        await http_manager.send_message_to_user(f'Новая сессия {_id}')
    async def on_session_removed(_id, _path):
        await http_manager.send_message_to_user(f'Сессия удалена {_id}')
    manager.on_session_new(on_session_new)
    manager.on_session_removed(on_session_removed)
    sessions = await manager.call_list_sessions()
    await http_manager.send_message_to_user(f'Текущие сессии: {sessions}')
    await asyncio.get_running_loop().create_future()


async def main():
    await look_sessions()


if __name__ == '__main__':
    asyncio.run(main())