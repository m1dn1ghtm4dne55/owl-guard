import logging
from typing import Dict, Any, Optional

from utils.logger.log_manager import get_logger


class SessionCacheService:
    def __init__(self):
        self._logger = get_logger()
        self._data: Dict[str, Dict[str, Any]] = {}

    def session_add(self, session_id: str, session_data: Dict[str, Any]):
        try:
            self._data[session_id] = session_data
            self._logger.debug(f"Session added in cache: {session_id}")
        except Exception as e:
            self._logger.error(f'Exception on cache session adder {e}')
            raise

    def session_get(self, session_id: str) -> Dict[str, Any]:
        session = self._data.get(session_id)
        if not session:
            self._logger.debug(f"Session not found in cache: {session_id}")
        return session

    def session_remove(self, session_id: str) -> bool:
        if self._data.pop(session_id, None) is not None:
            self._logger.debug(f"Session removed from cache: {session_id}")
            return True
        self._logger.debug(f"Session not in cache: {session_id}")
        return False

    def all_session_get_info(self) -> Optional[Dict[str, Dict[str, Any]]]:
        return self._data.copy()
