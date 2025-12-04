from logging import Formatter
from json import dumps
from datetime import datetime


class JSONFormatter(Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.threadName,
            'process': record.processName
        }
        return dumps(log_entry, ensure_ascii=False)