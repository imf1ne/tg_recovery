import datetime
import logging
import pytz
from telethon import events

from connector import DBworker
from messages import Message
from settings import SETTINGS


@events.register(events.NewMessage(func=lambda e: e.is_private))
async def handler_new_message(event):
    client = event.client
    try:
        await client.get_dialogs()
        logging.info(event.message)
        str_user_id = event.message.to_dict()['peer_id']
        user_id = int(str_user_id['user_id'])
        user = await client.get_entity(user_id)
        msg = Message(event, user)
        if not msg.out and msg.check_media():
            path_to_files = 'media/'
            await client.download_media(event.message,
                                        path_to_files + msg.media.filename)
        """Сохранение сообщения"""
        rez = DBworker.insert_new_messages(msg)
        logging.info(rez)
    except Exception as myEr:
        logging.warning(f'[-] New message Error: {myEr}')
    finally:
        """Обновление диалогов"""
        await client.get_dialogs()


@events.register(events.MessageDeleted)
async def handler_delete(event):
    client = event.client
    for msg_id in event.deleted_ids:
        try:
            del_date = datetime.datetime.now().astimezone(pytz.timezone(SETTINGS['TIMEZONE'])).replace(tzinfo=None)
            logging.info(f'Message {msg_id} was deleted in {event.chat_id}')
            my_message = dict(msg_id=msg_id, del_date=del_date)
            DBworker.insert_deleted_messages(my_message)
            """RESTORING"""
            rez = DBworker.restore_message(msg_id)
            logging.info(f'[*] Restoring - {rez}')
            if rez['result'] == 'OK':
                """Отправка восстановленно сообщения"""
                await client.send_message(SETTINGS['FAVORITES'], rez['text'],
                                          file=rez['filename'])
                logging.info('[+] Message was restored and sent!')
            else:
                logging.info(['[-] Error during restore!'])

        except Exception as e:
            logging.warning(f'[-] Restoring Error: {e}')
