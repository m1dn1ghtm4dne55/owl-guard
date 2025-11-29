from typing import Optional
from subprocess import run, PIPE


class SessionsLooker:
    def __init__(self):
        self._sessions_old: Optional[list[str]] = None
        self._ssh_users_count: int = 0

    def check_ssh_users_count(self, users_count: int) -> bool:
        if self._ssh_users_count != users_count:
            return False
        return True

    @property
    def get_ssh_user_count(self) -> int:
        return self._ssh_users_count

    def set_ssh_user_count(self, user_count_now: int):
        self._ssh_users_count = user_count_now

    def get_ssh_user_old(self):
        return self._sessions_old

    def get_login_users(self):
        users = run('loginctl', stdout=PIPE).stdout.decode()
        result = str(users).split('\n')[1:-3]
        self._sessions_old = result
        return result
