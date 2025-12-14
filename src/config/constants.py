from os import getenv, path, environ

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID = getenv('TELEGRAM_USER_ID')

CONFIG_PATH = path.join(path.dirname(__file__), 'logging.yaml')
LOG_FILE_PATH = environ.get('LOG_FILE_PATH', '/var/log/owl-guard.log')
WEBHOOK_URL = environ.get('WEBHOOK_URL', getenv('WEBHOOK_BOT_URL'))
LOG_FILE_MAX_BYTES = environ.get('LOG_FILE_MAX_BYTES', 524288000)
