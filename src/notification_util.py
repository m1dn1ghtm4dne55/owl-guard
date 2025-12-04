from aiohttp import ClientSession, TCPConnector

class AsyncMessageSender:
    def __init__(self, token: str, user_id: str, url:str = 'https://api.telegram.org/bot'):
        self._user_id = user_id
        self._url = f'{url}'
        self._token = token

    async def send_message_to_user(self, message):
        connector = TCPConnector(ssl=False)
        body = {"chat_id": self._user_id, "text": message}
        async with ClientSession(connector=connector) as session:
            response = await session.post(url=f'{self._url}{self._token}/sendMessage', data=body)
            response.raise_for_status()
            data = await response.json()
            return data