from telethon.sync import TelegramClient
from connector import DBworker
from events import handler_new_message, handler_delete
from settings import SETTINGS


if __name__ == "__main__":
    api_id = SETTINGS['api_id']
    api_hash = SETTINGS['api_hash']
    """Подготовка базы данных"""
    DBworker.create_tables()
    client = TelegramClient('Secret@Name$Session', api_id, api_hash)
    """Запуск API клиента и авторизация"""
    client.start()
    """Регистрация хендлеров"""
    client.add_event_handler(handler_new_message)
    client.add_event_handler(handler_delete)
    """Запуск"""
    client.run_until_disconnected()
