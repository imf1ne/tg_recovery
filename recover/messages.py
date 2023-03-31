import datetime
from media import *


class Message:
    def __init__(self, event, user):
        message_dict = event.message.to_dict()
        user_dict = user.to_dict()
        self.msg_id = int(message_dict['id'])
        self.out = message_dict['out']
        self.user_id = user_dict['id']
        self.username = user_dict['username']
        self.data = message_dict['message']
        self.first_name = user_dict['first_name']
        self.last_name = user_dict['last_name']
        self.phone = user_dict['phone']
        self.msg_date = datetime.datetime.now()
        self.media = message_dict['media']
        self.is_media = False
        self.is_media = bool(self.media)
        self.media = self.get_media(self.media, self.msg_id)
        self.is_reply = message_dict['reply_to']
        if self.is_reply:
            self.is_reply = int(self.is_reply['reply_to_msg_id'])

    def get_media(self, media, msg_id):
        if media:
            main_type = media['_']
            """Можно расширить типы сообщений"""
            if main_type == 'MessageMediaDocument':
                m = MessageMediaDocument(media, msg_id)
            elif main_type == 'MessageMediaPhoto':
                m = MessageMediaPhoto(media, msg_id)
            else:
                m = MediaUnknown(media, msg_id)
            return m
        else:
            m = MediaEmpty(media, msg_id)
            return m

    def check_media(self):
        if self.media.filename == 'Type-unknown.no':
            return 0
        elif self.media.size and self.media.size > 2000000:  # Это ограничение можно вручную убрать
            self.media.filename = 'Too_big_file'
            return 0
        elif self.media.filename is None:
            return 0
        else:
            return 1
