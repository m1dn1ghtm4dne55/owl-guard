from aiohttp import ClientResponseError
from aioresponses import aioresponses
import pytest

from utils.notification_utils import AsyncMessageSender


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status, raises, expected",
    [
        (200, False, {"ok": True, 'description': 'message send'}),
        (400, True, {"ok": False, "description": "Bad Request"}),
        (500, True, {"ok": False, "description": "Server Error"}),
    ]
)
async def test_send_message_success(status, raises, expected):
    sender = AsyncMessageSender("fake_token", "123")
    with aioresponses() as m:
        m.post("https://api.telegram.org/botfake_token/sendMessage", payload=expected, status=status)
        if raises:
            with pytest.raises(ClientResponseError):
                result = await sender.send_message_to_user("test message")
                assert result == expected
        else:
            result = await sender.send_message_to_user("test message")
            assert result == expected
