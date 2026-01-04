# Owl-Guard

Owl-Guard is a system login monitoring service for Linux servers. The tool captures authentication events and logins
from system journals, sends notifications via Telegram bot. The project is under development.

## Features

- Tracking all system logins
- Logging user login events
- Telegram notifications
- Log storage for analysis

## Installation

Automated installation with a single command:

```bash
wget https://raw.githubusercontent.com/m1dn1ghtm4dne55/owl-guard/refs/heads/master/install.sh -O install.sh && chmod +x install.sh && bash install.sh
```

The script sets up the service, dependencies, and prompts for Telegram bot token during installation.

## Requirements

- Linux with systemd
- Python 3.8+
- root access

## Usage

The service starts automatically

Logs: `/var/log/owl-guard.log`.

## CLI Commands

### Get value

```bash
owl-guard get <key>
```

### Set value

```bash
owl-guard set <key> <value>
```

### Invoke command line help

```bash
owl-guard get --help
owl-guard get -h

owl-guard set --help
owl-guard set -h
```

## License

MIT License.

**⚠️ Project under development — changes possible.**