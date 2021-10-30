import os
from telegram import Bot


BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROUP_CHATID = os.environ.get("CHAT_ID")


class Notifications():

    def __init__(self):
        self.my_cv_bot = Bot(token=BOT_TOKEN)

    def send_message(self, name, email, subject, message):
        self.my_cv_bot.sendMessage(chat_id=GROUP_CHATID,
                                   text=f"New MyCV Notification!!."
                                        f"\nName: {name}\nEmail: {email}\nSubject: {subject}\nMessage: {message}")
