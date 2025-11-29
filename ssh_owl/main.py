from os import getenv
from time import sleep
from datetime import datetime


from dotenv import load_dotenv

from sessions_looker import SessionsLooker
from notification_util import MessageSender

load_dotenv()

TOKEN = getenv('TOKEN')
USER_ID = getenv('USER_ID')
timeout = 1

http_manager = MessageSender(TOKEN, USER_ID)
session_manager = SessionsLooker()

if __name__ == '__main__':
    while True:
        sleep(timeout)
        ssh_users = session_manager.get_login_users()
        if session_manager.get_ssh_user_count == 0:
            session_manager.set_ssh_user_count(len(ssh_users))
            http_manager.send_message_to_user('SSH Owl запущена, текущие подключения:')
            for user in ssh_users:
                http_manager.send_message_to_user(user)
        else:
            if not session_manager.check_ssh_users_count(len(ssh_users)):
                count_difference = session_manager.get_ssh_user_count - len(ssh_users)
                session_manager.set_ssh_user_count(len(ssh_users))
                last_user = session_manager.get_ssh_user_old[-1]
                if count_difference > 0:
                    http_manager.send_message_to_user(f'{datetime.now()} | Отключился пользователь {last_user}\n')
                else:
                    http_manager.send_message_to_user(f'{datetime.now()} | Подключился пользователь {last_user}\n')