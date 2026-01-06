BRANCH="master"
REPO_URL=https://github.com/m1dn1ghtm4dne55/owl-guard/archive/refs/heads/${BRANCH}.zip
SERVICE_PATH=/opt/owl-guard
VENV_PATH="$SERVICE_PATH/venv"
ENV_PATH="$SERVICE_PATH/src/.env"

root_checker(){
  if [ "$(whoami)" != "root" ]; then
        echo "Please start me from root"
        exit 1
  fi
}

python_version_check() {
  local python_version=$(python3 -V 2>&1 | awk '{print $2}')
  local major_version=${python_version%%.*}
  local minor_version=${python_version#*.}
  local minor_version=${minor_version%%.*}
  if (( major_version < 3 || (major_version == 3 && minor_version < 10) )); then
    echo "For the program to work, you must update python version to 3.10+ (found $python_version)"
    exit 1
  fi
}

detect_pcg_manager() {
  if command -v dnf >/dev/null 2>&1; then
      PKG_MGR="dnf"
  elif command -v apt >/dev/null 2>&1; then
      PKG_MGR="apt"
  elif command -v yum >/dev/null 2>&1; then
      PKG_MGR="yum"
  elif command -v zypper >/dev/null 2>&1; then
      PKG_MGR="zypper"
  else
      echo "Unsupported Linux distribution no package manager found"
      exit 1
  fi
}

install_required_software() {
  local missing=()
  command -v unzip >/dev/null 2>&1 ||  missing+=("unzip")
  command -v pip  >/dev/null 2>&1 ||  missing+=("python3-pip")
  python3 -m venv --help >/dev/null 2>&1 || missing+=("python3-venv")
  if [ ${#missing[@]} -eq 0 ]; then
    return 0
  fi
  echo "Missing: ${missing[*]}. Install? (Y/y): "
  read -n 1 -r REPLY
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
      ${PKG_MGR} update
      ${PKG_MGR} install -y "${missing[@]}"
  else
    echo "Installation cancelled"
    exit 1
  fi
}

root_checker
python_version_check
detect_pcg_manager
install_required_software

echo "Getting file from repository"
if ! wget --quiet "${REPO_URL}" -O /tmp/owlguard.zip; then
  echo "No file on repository"
  exit 1
else
  echo "Files downloaded successfully"
fi

unzip -q -o /tmp/owlguard.zip -d  "${SERVICE_PATH}"

mv /opt/owl-guard/owl-guard-${BRANCH}/* /opt/owl-guard/
rm /tmp/owlguard.zip

cat >>"${ENV_PATH}" <<'EOF'
WEBHOOK_URL=''
LOG_FILE_MAX_BYTES='524288000'
LOG_FILE_PATH='/var/log/owl-guard.log'
DBUS_CORE_SESSION_TIMEOUT='2.0'
EOF

touch /var/log/owl-guard.log
rm -rf "${SERVICE_PATH}"/tests
rm -rf "${SERVICE_PATH}"/owl-guard-${BRANCH}/
rm -f "${SERVICE_PATH}"/{poetry.lock,pyproject.toml,pytest.ini}

read -rp "Enter you telegram bot token here: " TELEGRAM_BOT_TOKEN || true
if [ -n "${TELEGRAM_BOT_TOKEN}" ]; then
        echo "TELEGRAM_BOT_TOKEN='${TELEGRAM_BOT_TOKEN}'" >> "${ENV_PATH}"
fi
read -rp "Enter you telegram user id here: " TELEGRAM_USER_ID || true
if [ -n "${TELEGRAM_USER_ID}" ]; then
        echo "TELEGRAM_USER_ID='${TELEGRAM_USER_ID}'" >> "${ENV_PATH}"
fi
cp "${SERVICE_PATH}/owl-guard.service" /etc/systemd/system/

python3 -m venv "${VENV_PATH}"
source "${VENV_PATH}/bin/activate"

echo "Install requirements"
if [ -f "${SERVICE_PATH}/requirements.txt" ]; then
    pip install --upgrade pip -q
    pip install -r "${SERVICE_PATH}/requirements.txt" -q
    echo "Requirements have been successfully installed"
fi

cat > /usr/local/bin/owl-guard <<'EOF'
#!/bin/bash
VENV_PATH="/opt/owl-guard/venv"
cd /opt/owl-guard/src || exit 1
exec "${VENV_PATH}/bin/python" /opt/owl-guard/src/cli.py "$@"
EOF
chmod +x /usr/local/bin/owl-guard

systemctl daemon-reload
systemctl enable owl-guard.service
systemctl start owl-guard.service
echo "Owl-guard started"
echo "Complete"