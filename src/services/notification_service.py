import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from aiohttp import ClientResponseError
from pydantic import ValidationError

from utils.notification_utils import AsyncMessageSender, human_read_response
from models.schemas import LoginSessionShort
from utils.logger.log_manager import get_logger


class NotificationService(ABC):
    @abstractmethod
    async def session_new(self, payload: Dict[str, Any]):
        ...

    @abstractmethod
    async def _short_payload_getter(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def session_terminate(self, payload: Dict[str, Any]):
        ...

    @abstractmethod
    async def all_active_session(self, payload: Dict[str, Any]):
        ...


class TelegramNotificationHandler(NotificationService):
    def __init__(self, token: str, user_id: str):
        self._http_manager = AsyncMessageSender(token, user_id)
        self._logger = get_logger()

    async def _short_payload_getter(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            payload = LoginSessionShort(**payload)
            return payload.model_dump()
        except ValidationError as e:
            self._logger.error(f'Asyncio ValidationError in payload_getter {e}')
            raise
        except Exception as e:
            self._logger.error(f'Exception {e}')
            raise

    async def session_new(self, payload: Dict[str, Any]):
        try:
            short_payload = await self._short_payload_getter(payload=payload)
            body = human_read_response(payload=short_payload)
            self._logger.info('User {} open session {}'.format(short_payload.get('name'), short_payload.get('id')))
            await self._http_manager.send_message_to_user(body)
        except ClientResponseError as e:
            logging.error(f'Error send message to Telegram in session new {e}')
        except Exception as e:
            self._logger.error(f'Exception {e}')
            raise


    async def session_terminate(self, payload: Dict[str, Any]):
        try:
            short_payload = await self._short_payload_getter(payload=payload)
            body = human_read_response(payload=short_payload)
            self._logger.info('User {} terminate session {}'.format(short_payload.get('name'), short_payload.get('id')))
            await self._http_manager.send_message_to_user(body)
        except ClientResponseError as e:
            logging.error(f'Error send message to Telegram in session terminate {e}')
        except Exception as e:
            self._logger.error(f'Exception {e}')
            raise

    async def all_active_session(self, payload: Dict[str, Any]):
        ...
