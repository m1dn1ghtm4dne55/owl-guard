import argparse

parser = argparse.ArgumentParser()


def get_telegram_token(args: argparse.Namespace):
    with open('.env', 'r') as file:
        print(file.read())


def set_telegram_token(args: argparse.Namespace):
    with open('.env', 'w') as w_file:
        w_file.write(f"TELEGRAM_BOT_TOKEN='{args.token}'")


def cli():
    subparser = parser.add_subparsers(required=True)
    p_get = subparser.add_parser("get_token", help="Get info Telegram bot token")
    p_get.set_defaults(func=get_telegram_token)
    p_set = subparser.add_parser("set_token", help="Set Telegram bot token")
    p_set.add_argument("token", help="Telegram token")
    p_set.set_defaults(func=set_telegram_token)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    cli()
