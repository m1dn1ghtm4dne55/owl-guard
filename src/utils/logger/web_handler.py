import asyncio
from logging import Handler, getLogger

from aiohttp import ClientSession, TCPConnector, ClientTimeout, ClientConnectionError, ServerDisconnectedError
from typing import Optional, Dict, Any
from json import loads


class WebhookHandler(Handler):
    def __init__(self, webhook_url: str, timeout: int = 10, max_queue_size: int = 300):
        super().__init__()
        self._webhook_url = webhook_url
        self._timeout = timeout
        self._queue = asyncio.Queue(maxsize=max_queue_size)
        self._sender_task: Optional[asyncio.Task] = None
        self._started = False
        self._fallback_logger = getLogger(f"{__name__}.webhook_fallback")
        self._session: Optional[ClientSession] = None
        self._session_lock = asyncio.Lock()

    def _start(self):
        if not self._started and self._sender_task is None:
            self._sender_task = asyncio.create_task(self._queue_processor())
            self._started = True

    def emit(self, record):
        try:
            payload: Dict[str, Any] = loads(self.format(record))
            self._queue.put_nowait(payload)
            self._start()
        except asyncio.QueueFull:
            self._fallback_logger.error(f"Очередь переполнена")
        except Exception as e:
            self._fallback_logger.error(f"Ошибка при добавлении в очередь: {e}")

    async def _session_get(self) -> ClientSession:
        async with self._session_lock:
            if self._session is None or self._session.closed:
                connector = TCPConnector(ssl=False)
                self._session = ClientSession(
                    connector=connector,
                    timeout=ClientTimeout(total=self._timeout)
                )
                self._fallback_logger.debug("Создана новая сессия")
            return self._session

    async def _session_close(self):
        async with self._session_lock:
            if self._session and not self._session.closed:
                await self._session.close()
                self._session = None
                self._fallback_logger.debug('Сессия закрыта')

    async def _send_webhook(self, payload: Dict[str, Any]) -> Optional[int]:
        try:
            session = await self._session_get()
            async with session.post(self._webhook_url, json=payload) as response:
                if response.status != 200:
                    response_message = await response.text()
                    self._fallback_logger.error(f"Ошибка отправки: {response.status} {response_message}")
                return response.status
        except ClientConnectionError as e:
            await self._session_close()
            self._fallback_logger.error(f'Проблемы с соеденением, сессия закрыта {e}')
        except asyncio.TimeoutError:
            self._fallback_logger.error(f"Таймаут при отправке")
        except Exception as e:
            self._fallback_logger.error(f"Ошибка при отправке: {e}")

    async def _queue_processor(self):
        while self._started or not self._queue.empty():
            try:
                try:
                    payload = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    if self._queue.empty():
                        break
                    continue
                await self._send_webhook(payload)
                self._queue.task_done()
                await asyncio.sleep(0.2)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._fallback_logger.error(f'Ошибка в процессоре очереди {e}')
                self._queue.task_done()
                await asyncio.sleep(1)
        await self._process_remaining_messages()

    async def _process_remaining_messages(self):
        try:
            while not self._queue.empty():
                try:
                    payload = self._queue.get_nowait()
                    await self._send_webhook(payload)
                    self._queue.task_done()
                except asyncio.QueueEmpty:
                    break
        finally:
            await self._session_close()
            self._drop_all_started_flags()

    def _drop_all_started_flags(self):
        self._started = False
        self._sender_task = None

    async def _emergency_stop(self):
        if self._sender_task and not self._sender_task.done():
            self._sender_task.cancel()
            await self._session_close()
            self._drop_all_started_flags()
        await self._process_remaining_messages()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._emergency_stop()
