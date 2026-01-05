from argparse import ArgumentParser, Namespace

from config.constants import HELP_INFO
from services.env_service import env_service
from utils.cli_validator import CLIValidator


def handle_env(args: Namespace) -> None:
    key = args.key.upper()
    cli_validator = CLIValidator(args)
    value = cli_validator.validate
    if value:
        if args.command == "get":
            print(env_service.get_env_value(key=key))
        elif args.command == "set":
            if value:
                env_service.set_env_value(key=key, line=args.value)
                print('To make changes you need to restart the owl-guard.service')


def cli() -> None:
    parser = ArgumentParser()
    sub_parser = parser.add_subparsers(required=True, dest="command")
    for cmd in ("get", "set"):
        cmd_line_parser = sub_parser.add_parser(cmd, help=f"{cmd} env value")
        cmd_line_parser.add_argument("key", help=f"{[value.lower() for value in env_service.get_env_keys()]}")
        if cmd == "set":
            cmd_line_parser.add_argument("value",
                                         help=HELP_INFO)
        cmd_line_parser.set_defaults(func=handle_env)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    cli()
