from argparse import ArgumentParser, Namespace

from services.env_service import env_service


def handle_env(args: Namespace):
    if args.command == "get":
        print(env_service.get_env_value(key=args.key))
    elif args.command == "set":
        env_service.set_env_value(key=args.key, line=args.value)


def cli():
    parser = ArgumentParser()
    sub_parser = parser.add_subparsers(required=True, dest="command")
    for cmd in ("get", "set"):
        cmd_line_parser = sub_parser.add_parser(cmd, help=f"{cmd} env value")
        cmd_line_parser.add_argument("key", help=f"{env_service.get_env_keys()}")
        if cmd == "set":
            cmd_line_parser.add_argument("value", help="New value")
        cmd_line_parser.set_defaults(func=handle_env)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    cli()
