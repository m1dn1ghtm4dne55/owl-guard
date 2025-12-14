# Owl-Guard

Owl-Guard is a system login monitoring service for Linux servers. The tool captures authentication events and logins from system journals, sends notifications via Telegram bot. The project is under development.

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

The service starts automatically:

```bash
systemctl status owl-guard
```

Logs: `/var/log/owl-guard.log`.

## License

MIT License.

**⚠️ Project under development — changes possible.**
