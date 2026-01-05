from datetime import datetime
from inspect import stack
from typing import Any

from aiohttp import ClientSession

class AsyncMessageSender:
    def __init__(self, token: str, user_id: str, url:str = 'https://api.telegram.org/bot'):
        self._user_id = user_id
        self._url = f'{url}'
        self._token = token

    async def send_message_to_user(self, message) -> dict[str, Any]:
        body = {"chat_id": self._user_id, "text": message}
        async with ClientSession() as session:
            response = await session.post(url=f'{self._url}{self._token}/sendMessage', data=body)
            response.raise_for_status()
            data = await response.json()
            return data


def human_read_response(payload: dict) -> str:
    lines = []
    source_func = stack()[1].function.replace('_', ' ')
    for key, value in payload.items():
        if key == 'timestamp':
            dt = datetime.fromtimestamp(value / 1000000)
            lines.append(f'{key}: {dt.strftime("%Y-%m-%d %H:%M:%S")}')
        else:
            lines.append(f'{key}: {value}')
    result = '\n'.join(lines)
    return f'{source_func}\n\n{result}'