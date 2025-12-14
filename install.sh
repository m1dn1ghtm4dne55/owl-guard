#!/usr/bin/env bash
REPO_URL=https://github.com/m1dn1ghtm4dne55/owl-guard/archive/refs/heads/master.zip
SERVICE_PATH=/opt/owl-guard
VENV_PATH="$SERVICE_PATH/venv"
ENV_PATH="$SERVICE_PATH/src/.env"

if [ "$(whoami)" != "root" ]; then
        echo "Please start me from root"
        exit
fi

echo "Start getting file fron repository"
if ! wget  "$REPO_URL" -O /tmp/logger.zip; then
  echo "No file on repository"
  exit
fi

unzip -q -o /tmp/logger.zip -d  "$SERVICE_PATH"
mv /opt/owl-guard2/owl-guard-master/* /opt/owl-guard2/
rmdir "$SERVICE_PATH"/owl-guard-master
rm /tmp/logger.zip
touch "$ENV_PATH"


read -rp "Enter you telegram bot token here: " TELEGRAM_BOT_TOKEN || true
if [ -n "${TELEGRAM_BOT_TOKEN}" ]; then
        echo "TELEGRAM_BOT_TOKEN='${TELEGRAM_BOT_TOKEN}'" >> "$ENV_PATH"
fi
read -rp "Enter you telegram user id here: " TELEGRAM_USER_ID || true
if [ -n "${TELEGRAM_USER_ID}" ]; then
        echo "TELEGRAM_USER_ID='${TELEGRAM_USER_ID}'" >> "$ENV_PATH"
fi
cp "$SERVICE_PATH/owl-guard.service" /etc/systemd/system/
echo "service unit create"


echo "Create virtualenv"
python3 -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"

echo "Install requirements"
if [ -f "$SERVICE_PATH/requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r "$SERVICE_PATH/requirements.txt"
fi

systemctl daemon-reload
echo "systemd reload"
systemctl enable owl-guard.service
systemctl start owl-guard.service
echo "ssh-owl start"