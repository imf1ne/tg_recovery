import datetime
import logging
import pytz
import sqlite3
from settings import SETTINGS


create_new_messages = '''CREATE TABLE if not exists new_messages(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                msg_id INTEGER NOT NULL,
                                is_output_msg BOOL, 
                                is_reply INTEGER,
                                username text,
                                data text,
                                first_name text,
                                last_name text,
                                phone text,
                                msg_date datetime,
                                is_media INTEGER,
                                filename text,
                                size INTEGER);'''

create_edited_messages = '''CREATE TABLE if not exists edited_messages(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                msg_id INTEGER NOT NULL,
                                is_output_msg BOOL,
                                username text,
                                last_data text,
                                new_data text,
                                is_media INTEGER,
                                msg_date datetime,
                                edit_date datetime);'''

create_deleted_messages = '''CREATE TABLE if not exists deleted_messages(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                msg_id INTEGER NOT NULL,
                                del_date datetime);'''

create_recovery_messages = '''CREATE TABLE if not exists recovered_messages(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                msg_id INTEGER NOT NULL,
                                username text,
                                data text,
                                is_media INTEGER,
                                msg_date datetime,
                                del_date datetime);'''

logging.basicConfig(level=logging.INFO,
                    filename="recover-bot.log",
                    filemode="a",
                    format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s')


class DBworker:
    @staticmethod
    def connect():
        try:
            sqlite_connection = sqlite3.connect('database.sqlite3')
            sqlite_connection.row_factory = sqlite3.Row
            cursor = sqlite_connection.cursor()
            return sqlite_connection, cursor
        except sqlite3.Error as error:
            logging.error("[-] Ошибка при подключении к sqlite", error)
            if (sqlite_connection):
                sqlite_connection.close()

    @staticmethod
    def disconnect(sqlite_connection):
        try:
            if (sqlite_connection):
                sqlite_connection.close()
            logging.info("[*] Соединение с базой данных закрыто")

        except Exception as Err:
            logging.error("[-] Ошибка при отключении от базы", Err)
        finally:
            if (sqlite_connection):
                sqlite_connection.close()

    @classmethod
    def create_tables(cls):
        try:
            sqlite_connection, cursor = cls.connect()
            queryes = [create_new_messages,
                       create_edited_messages,
                       create_deleted_messages,
                       create_recovery_messages]
            for q in queryes:
                cursor.execute(q)
            sqlite_connection.commit()
            cursor.close()

        except Exception as Err:
            logging.error("[-] Ошибка при создании таблиц", Err)

        finally:
            cls.disconnect(sqlite_connection)

    @classmethod
    def insert(cls, query, *args):
        try:
            sqlite_connection, cursor = cls.connect()
            cursor.execute(query, args)
            sqlite_connection.commit()
            return "OK"
        except Exception as Err:
            logging.error(f"[-] Ошибка при всталении данных: {Err}")

        finally:
             cls.disconnect(sqlite_connection)

    @classmethod
    def select(cls, query, *args):
        try:
            sqlite_connection, cursor = cls.connect()
            cursor.execute(query, args)
            sqlite_connection.commit()
            return cursor.fetchall()[0]
        except Exception as IndexError:
            return 'select error'
        except Exception as Err:
            logging.error(f"[-] Ошибка при запросе данных: {Err}")
            return 'select error'
        finally:
            cls.disconnect(sqlite_connection)

    @classmethod
    def insert_new_messages(cls, my_message):
        query = ''' INSERT INTO new_messages(
                    msg_id, is_output_msg, is_reply, username,
                    data, first_name, last_name, phone,
                    msg_date, is_media, filename, size
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?);'''

        msg_date = my_message.msg_date.astimezone(pytz.timezone(SETTINGS['TIMEZONE'])).replace(tzinfo=None)
        rez = cls.insert(query, my_message.msg_id, my_message.out,
                         my_message.is_reply, my_message.username,
                         my_message.data, my_message.first_name,
                         my_message.last_name, my_message.phone,
                         msg_date, my_message.is_media,
                         my_message.media.filename, my_message.media.size)
        if rez == 'OK':
            return '[+] Message saved successfuly!'
        else:
            return rez

    @classmethod
    def insert_deleted_messages(cls, my_message):
        query = '''INSERT INTO deleted_messages(msg_id, del_date)
                    VALUES (?,?);'''
        rez = cls.insert(query, my_message['msg_id'], my_message['del_date'])
        if rez == 'OK':
            return '[*] Message was deleted!'
        else:
            return rez

    @classmethod
    def restore_message(cls, msg_id):
        q = ''' SELECT is_output_msg, username, first_name,
                last_name, phone, data, msg_date,
                is_media, filename, size FROM new_messages
                 WHERE msg_id = (?)'''
        record = cls.select(q, msg_id)
        if record != 'select error':
            out = record['is_output_msg']
            username = record['username']
            first_name = record['first_name'] or ''
            last_name = record['last_name'] or ''
            phone = record['phone'] or 'Номер скрыт'
            data = f"📝Текст: {record['data']}\n" if record['data'] else ''
            msg_date = datetime.datetime.strptime(record['msg_date'],
                                                  '%Y-%m-%d %H:%M:%S.%f')
            msg_date = msg_date.strftime('%d.%m.%Y %H:%M:%S')
            is_media = record['is_media']
            filename = record['filename']
            del_date = datetime.datetime.now().astimezone(pytz.timezone(SETTINGS['TIMEZONE'])).replace(tzinfo=None)
            del_date = del_date.strftime('%d.%m.%Y %H:%M:%S')
            if not out:  # if input message
                query = '''INSERT INTO recovered_messages(msg_id, username,
                           data, is_media, msg_date, del_date)
                           VALUES (?,?,?,?,?,?);'''
                rez = cls.insert(query, msg_id, username, data,
                                 is_media, msg_date, del_date)
                if rez == 'OK':
                    if filename == 'Type-unknown.no':
                        file = None
                        description = '💾 В сообщении был файл. '\
                                      'Данный формат файла не поддерживается\n'
                    elif filename == 'Too_big_file':
                        file = None
                        description = '💾 В сообщении файл превышающий 2Мб,'\
                                      ' файл не был восстановлен\n'
                    elif filename is None:
                        description = ''
                        file = None
                    else:
                        description = '💾 Файл успешно восстановлен!\n'
                        file = 'media/' + filename
                    text = f'❗УДАЛЕНИЕ❗\n👤{first_name} {last_name}\n'\
                           f'📞Phone: {phone}\n{data}{description}'\
                           f'🕐Отправлено: {msg_date}\n🕒Удалено: {del_date}'
                    return {'result': 'OK', 'command': 'delete',
                            'text': text, 'filename': file}
                else:
                    return {'result': 'NO', 'text': rez}
            else:
                return {'result': 'NO', 'text': '[*] Message is output'}
        else:
            return {'result': 'NO', 'text': '[*] Message not found'}
