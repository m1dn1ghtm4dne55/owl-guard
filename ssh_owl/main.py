from os import getenv

from notification_util import MessageSender
from dotenv import load_dotenv

load_dotenv()

TOKEN = getenv('TOKEN')
USER_ID = getenv('USER_ID')

manager = MessageSender(TOKEN, USER_ID)
manager.send_message_to_user('Я из бубунты')

if __name__ == '__main__':
    pass