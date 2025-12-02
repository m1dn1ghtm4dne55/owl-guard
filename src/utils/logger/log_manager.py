from os.path import exists

from logging import config, getLogger
from functools import lru_cache
from yaml import safe_load

from utils.logger.constants import LOG_FILE_PATH, WEBHOOK_URL, LOG_FILE_MAX_BYTES, CONFIG_PATH


class LoggerConfiguration:
    _configurate = False

    @classmethod
    def logging_setup(cls, config_file):
        if not cls._configurate:
            if not exists(config_file):
                raise FileNotFoundError(f'Отсутствует конфигурационный файл {config_file}')
            if not getLogger().handlers:
                with open(config_file, 'r') as r_file:
                    config_content = r_file.read().format(
                        WEBHOOK_URL=WEBHOOK_URL,
                        LOG_FILE_PATH=LOG_FILE_PATH,
                        LOG_FILE_MAX_BYTES=LOG_FILE_MAX_BYTES
                    )
                    config_dict = safe_load(config_content)
                    config.dictConfig(config_dict)
            cls._configurate = True


class LoggerManager:
    def __init__(self, logger_name: str = None):
        if logger_name is None:
            self._logger = getLogger(__name__)
        else:
            self._logger = getLogger(logger_name)

    def __getattr__(self, name):
        return getattr(self._logger, name)


@lru_cache(maxsize=128)
def get_logger(logger_name: str = None) -> LoggerManager:
    LoggerConfiguration.logging_setup(CONFIG_PATH)
    return LoggerManager(logger_name)
