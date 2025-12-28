from typing import Optional
from argparse import Namespace, ArgumentParser


def read_env(env_path: str) -> list[str]:
    with open(env_path, 'r') as file:
        lines = file.readlines()
        return lines


def write_env(new_data: list[str], env_path: str):
    with open(env_path, 'w') as file:
        file.writelines(new_data)


def get_env_value(key: str, env_path: str) -> Optional[str]:
    lines = read_env(env_path)
    for line in lines:
        if line.startswith(key):
            value = line.split('=')[-1].strip()
            if value[0] and value[-1] == "'":
                value = value[1:-1]
                return value
            return value
    return None


def set_env_value(key: str, line: str, env_path: str) -> list[str]:
    lines = read_env(env_path)
    new_line = f"{key}='{line}'\n"
    for i, line in enumerate(lines):
        if line.startswith(key):
            lines[i] = new_line
            break
    else:
        lines.append(new_line)
    write_env(env_path=env_path, new_data=lines)
    return lines


def cmd_set_telegram_token(args: Namespace):
    set_env_value(env_path='.env', key=args.key, line=args.value)


def cmd_get_telegram_token(args: Namespace):
    print(get_env_value(env_path='.env', key=args.key))


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
