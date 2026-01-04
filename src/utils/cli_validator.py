from argparse import Namespace
from re import compile

from services.env_service import env_service


class CLIValidator:
    INTEGER_KEYS = {'LOG_FILE_MAX_BYTES', 'TELEGRAM_USER_ID'}
    FLOAT_KEYS = {'DBUS_CORE_SESSION_TIMEOUT'}
    TELEGRAM_TOKEN_KEY = {'TELEGRAM_BOT_TOKEN'}
    TELEGRAM_TOKEN_PATTERN = compile(r'^[0-9]{8,10}:[A-Za-z0-9_-]{35}$')

    def __init__(self, args: Namespace):
        self.all_keys = {k.upper() for k in env_service.get_env_keys()}
        self.args = args

    @staticmethod
    def _validate_key_isdigit(args_value) -> str:
        if args_value.isdigit():
            return args_value
        raise ValueError('must be integer')

    @staticmethod
    def _validate_key_float(args_value) -> str:
        try:
            value = float(args_value)
            return str(value)
        except ValueError:
            raise ValueError('must be float or integer')

    @staticmethod
    def _validate_telegram_bot_token(args_value) -> str:
        if CLIValidator.TELEGRAM_TOKEN_PATTERN.match(args_value):
            return args_value
        raise ValueError('invalid')

    def _get_validator(self, key: str):
        if key in self.INTEGER_KEYS:
            return self._validate_key_isdigit
        if key in self.TELEGRAM_TOKEN_KEY:
            return self._validate_telegram_bot_token
        if key in self.FLOAT_KEYS:
            return self._validate_key_float
        raise ValueError('unknown key type')

    @property
    def validate(self) -> bool:
        args_key = self.args.key.upper()
        if args_key not in self.all_keys:
            print(f'Invalid argument, please use arguments from array -> {[value.lower() for value in self.all_keys]}')
            return False
        try:
            args_value = self.args.value
        except AttributeError:
            return True
        try:
            self._get_validator(args_key)(args_value)
            return True
        except ValueError as e:
            print(f'{args_key.lower()} {e}')
            return False



