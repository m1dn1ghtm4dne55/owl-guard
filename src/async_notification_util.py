from os import getenv

from dotenv import load_dotenv
from aiohttp import ClientSession, TCPConnector

load_dotenv()

TOKEN = getenv('TOKEN')
USER_ID = getenv('USER_ID')


class AsyncMessageSender:
    def __init__(self, token: str, user_id: str):
        self._user_id = user_id
        self._url = f'https://api.telegram.org/bot{token}/SendMessage'

    async def send_message_to_user(self, message):
        connector = TCPConnector(ssl=False)
        body = {"chat_id": self._user_id, "text": message}
        async with ClientSession(connector=connector) as session:
            response = await session.post(url=self._url, data=body)
