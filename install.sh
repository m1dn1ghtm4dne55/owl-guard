#!/usr/bin/env bash
REPO_URL=https://github.com/m1dn1ghtm4dne55/owl-guard/archive/refs/heads/master.zip
SERVICE_PATH=/opt/owl-guard/
ENV_PATH="$SERVICE_PATH/src/.env"

if [ "$(whoami)" != "root" ]; then
        echo "Please start me from root"
        exit
fi

if ! wget -q "$REPO_URL" -O /tmp/logger.zip; then
  echo "No file on repository"
  exit
fi
unzip -q -o /tmp/logger.zip -d  "$SERVICE_PATH"
rm /tmp/logger.zip
touch "$ENV_PATH"


read -rp "TELEGRAM_BOT_TOKEN: " TELEGRAM_BOT_TOKEN || true
if [ -n "${TELEGRAM_BOT_TOKEN}" ]; then
        echo "TELEGRAM_BOT_TOKEN='${TELEGRAM_BOT_TOKEN}'" >> "$ENV_PATH"
fi
read -rp "TELEGRAM_USER_ID: " TELEGRAM_USER_ID || true
if [ -n "${TELEGRAM_USER_ID}" ]; then
        echo "TELEGRAM_USER_ID='${TELEGRAM_USER_ID}'" >> "$ENV_PATH"
fi

cp "$SERVICE_PATH/owl-guard.service" /etc/systemd/system/