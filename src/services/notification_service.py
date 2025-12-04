from abc import ABC, abstractmethod
from typing import Dict, Any

from pydantic import ValidationError

from utils.notification_utils import AsyncMessageSender, human_read_response
from models.schemas import LoginSessionShort
from utils.logger.log_manager import get_logger


class NotificationService(ABC):
    @abstractmethod
    async def session_new(self, payload: Dict[str, Any]):
        ...

    @abstractmethod
    async def session_removed(self, _id: str, _path: str):
        ...

    @abstractmethod
    async def all_active_session(self, payload: Dict[str, Any]):
        ...


class TelegramNotificationHandler(NotificationService):
    def __init__(self, token: str, user_id: str):
        self._http_manager = AsyncMessageSender(token, user_id)
        self._logger = get_logger("dev")

    async def session_new(self, payload: Dict[str, Any]):
        try:
            model = LoginSessionShort(**payload)
            response = human_read_response(payload=model.model_dump())
            self._logger.info(f'User {model.name} open session {model.id}')
            await self._http_manager.send_message_to_user(response)
        except ValidationError as e:
            self._logger.error(f'Asyncio ValidationError in on new session {e}')
            raise
        except Exception as e:
            self._logger.error(f'Exception {e}')
            raise

    async def session_removed(self, _id: str, _path: str):
        self._logger.info(f'{_id, _path}')
        # await self._http_manager.send_message_to_user()

    async def all_active_session(self, payload: Dict[str, Any]):
        try:
            model = LoginSessionShort(**payload)
            response = human_read_response(payload=model.model_dump())
            self._logger.info(f'User {model.name} open session {model.id}')
            await self._http_manager.send_message_to_user(response)
        except ValidationError as e:
            self._logger.error(f'Asyncio ValidationError in on new session {e}')
            raise
        except Exception as e:
            self._logger.error(f'Exception {e}')
            raise