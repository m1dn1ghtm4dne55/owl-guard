from datetime import datetime


def human_read_response(payload: dict):
    lines = []
    for key, value in payload.items():
        if key == 'timestamp':
            dt = datetime.fromtimestamp(value / 1000000)
            lines.append(f'{key}: {dt.strftime("%Y-%m-%d %H:%M:%S")}')
        else:
            lines.append(f'{key}: {value}')
    result = '\n'.join(lines)
    return f'New login\n\n{result}'