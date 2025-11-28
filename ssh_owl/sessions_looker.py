from typing import Optional


class SessionsLooker:
    def __init__(self, sleep_time:int = 1):
        self.sleep_time = sleep_time
        self._sessions_now: Optional[list[str]] = None
        self._sessions_old: Optional[list[str]] = None
        self._ssh_users_count: int = 0

    def check_ssh_users_count(self, users_count: int) -> bool:
        if self._ssh_users_count != users_count:
            return False
        return True

    def get_ssh_user_count(self):
        return self._ssh_users_count

    def get_ssh_user_now(self):
        return self._sessions_now

    def get_ssh_user_old(self):
        return self._sessions_old