from asyncio import run

from dbus_core import LogingBusPooler


async def main():
    dbus_pooler = LogingBusPooler()
    await dbus_pooler.look_sessions()


if __name__ == '__main__':
    run(main())
