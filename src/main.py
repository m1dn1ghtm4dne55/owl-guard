from asyncio import run

from constants import TOKEN, USER_ID
from dbus_core import DBusConnector, LoginSessionService
from login_monitor import LoginMonitor
from notification_service import TelegramNotificationHandler


async def main():
    dbus = DBusConnector()
    session_service = LoginSessionService(dbus)
    telegram_notification = TelegramNotificationHandler(TOKEN, USER_ID)
    monitor = LoginMonitor(dbus, session_service, telegram_notification)

    await monitor.run_monitoring()

if __name__ == "__main__":
    run(main())
