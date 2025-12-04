from os import getenv, path, environ

from dotenv import load_dotenv

load_dotenv()

TOKEN = getenv('TOKEN')
USER_ID = getenv('USER_ID')

CONFIG_PATH = path.join(path.dirname(__file__), 'logging.yaml')
LOG_FILE_PATH = environ.get('LOG_FILE_PATH', 'utils/logger/bot.log')
WEBHOOK_URL = environ.get('WEBHOOK_URL', getenv('WEBHOOK_BOT_URL'))
LOG_FILE_MAX_BYTES = environ.get('LOG_FILE_MAX_BYTES', 524288000)
