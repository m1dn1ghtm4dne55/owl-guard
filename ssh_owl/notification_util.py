import json
from contextlib import contextmanager
from typing import Any, Generator

from urllib3 import PoolManager


class MessageSender:
    def __init__(self, token: str, user_id: str):
        self._user_id = user_id
        self._url = f'https://api.telegram.org/bot{token}'
        self._pool_manager = PoolManager()

    @contextmanager
    def session(self) -> Generator[PoolManager, Any, None]:
        try:
            yield self._pool_manager
        except Exception as e:
            print(f'Ошибка при создании сессии {e}')

    def send_message_to_user(self, message):
        body = json.dumps({"chat_id": self._user_id, "text": message}).encode("utf-8")
        with self.session() as session:
            try:
                response = session.request(method="POST", url=f'{self._url}/sendMessage',
                                body=body, headers={"Content-Type": "application/json"})
                if response.status != 200:
                    print(response.status)
            except Exception as e:
                print(f'Ошибка при отправке сообщения {e}')

