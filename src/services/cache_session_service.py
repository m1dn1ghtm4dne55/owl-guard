from typing import Dict, Any


class SessionCacheService:
    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}

    def session_add(self, session_id: str, session_data: Dict[str, Any]):
        self._data[session_id] = session_data

    def session_get(self, session_id: str):
        return self._data.get(session_id)
    def session_remove(self, session_id: str):
        self._data.pop(session_id)

    def all_session_get_info(self):
        return self._data
