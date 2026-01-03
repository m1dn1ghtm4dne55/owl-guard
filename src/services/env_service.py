from typing import Optional


class EnvService:
    def __init__(self, env_path):
        self.env_path = env_path

    def read_env(self) -> list[str]:
        with open(self.env_path, 'r') as file:
            lines = file.readlines()
            return lines

    def write_env(self, new_data: list[str]):
        with open(self.env_path, 'w') as file:
            file.writelines(new_data)

    def get_env_value(self, key: str) -> Optional[str]:
        lines = self.read_env()
        for line in lines:
            if line.startswith(key):
                value = line.split('=')[-1].strip()
                if value[0] and value[-1] == "'":
                    value = value[1:-1]
                    return value
                return value
        return None

    def set_env_value(self, key: str, line: str) -> list[str]:
        lines = self.read_env()
        new_line = f"{key}='{line}'\n"
        for i, line in enumerate(lines):
            if line.startswith(key):
                lines[i] = new_line
                break
        else:
            lines.append(new_line)
        self.write_env(new_data=lines)
        return lines

    def get_env_keys(self) -> list[str]:
        lines = self.read_env()
        keys = [line.split('=')[0] for line in lines]
        return keys

env_service = EnvService('.env')
