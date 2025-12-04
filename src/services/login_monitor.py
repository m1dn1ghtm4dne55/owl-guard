from dbus_next import DBusError

from core.dbus import DBusConnector, LoginSessionService
from services.notification_service import NotificationService
from utils.logger.log_manager import get_logger


class LoginMonitor:
    def __init__(self, dbus: DBusConnector, session_service: LoginSessionService, notify_service: NotificationService):
        self._dbus = dbus
        self._logger = get_logger('dev')
        self._session = session_service
        self._notify = notify_service

    async def _on_session_new(self, session_id: str, path: str) -> None:
        payload = await self._session.get_session_property(session_id, path)
        await self._notify.session_new(payload)

    async def _on_session_removed(self, session_id: str, path: str) -> None:
        await self._notify.session_removed(session_id, path)

    async def _sessions_info(self, sessions: list):
        for sess in sessions:
            payload = await self._session.get_session_property(session_id=sess[0], path=sess[-1])
            await self._notify.all_active_session(payload)

    async def run_monitoring(self):
        try:
            self._logger.info('Start monitoring loging session')
            manager_interface = await self._session.get_manager_interface()
            sessions = await manager_interface.call_list_sessions()
            self._logger.info(f'List active session {sessions}')
            await self._sessions_info(sessions)
            manager_interface.on_session_new(self._on_session_new)
            manager_interface.on_session_removed(self._on_session_removed)
            await self._dbus.wait_for_shutdown()
        except DBusError as e:
            self._logger.error(f'DBus error in look session pooler {e}')
            raise
