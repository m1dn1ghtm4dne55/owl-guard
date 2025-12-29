from argparse import Namespace, ArgumentParser

from services.env_service import env_service


def cmd_set_telegram_token(args: Namespace):
    env_service.set_env_value(key=args.key, line=args.value)


def cmd_get_telegram_token(args: Namespace):
    print(env_service.get_env_value(key=args.key))


def cli():
    parser = ArgumentParser()
    sub_parser = parser.add_subparsers(required=True)
    p_get = sub_parser.add_parser("get", help="Get new value")
    p_get.add_argument("key", help="TELEGRAM_BOT_TOKEN or TELEGRAM_USER_ID")
    p_get.set_defaults(func=cmd_get_telegram_token)
    p_set = sub_parser.add_parser("set", help="Set new value")
    p_set.add_argument("key", help="TELEGRAM_BOT_TOKEN or TELEGRAM_USER_ID")
    p_set.add_argument("value", help="New value for TELEGRAM_BOT_TOKEN or TELEGRAM_USER_ID")
    p_set.set_defaults(func=cmd_set_telegram_token)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    cli()
