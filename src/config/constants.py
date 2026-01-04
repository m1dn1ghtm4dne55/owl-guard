from os import getenv, path, environ

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID = getenv('TELEGRAM_USER_ID')

CONFIG_PATH = path.join(path.dirname(__file__), 'logging.yaml')
LOG_FILE_PATH = environ.get('LOG_FILE_PATH', '/var/log/owl-guard.log')
WEBHOOK_URL = environ.get('WEBHOOK_URL', getenv('WEBHOOK_BOT_URL'))
LOG_FILE_MAX_BYTES = int(environ.get('LOG_FILE_MAX_BYTES', 524288000))
DBUS_CORE_SESSION_TIMEOUT = float(environ.get('DBUS_CORE_SESSION_TIMEOUT', 2.0))

HELP_INFO = 'LOG_FILE_MAX_BYTES is integer | TELEGRAM_USER_ID is integer | TELEGRAM_BOT_TOKEN is token | WEBHOOK_URL is url | LOG_FILE_PATH is path | DBUS_CORE_SESSION_TIMEOUT is float or integer'
