# tg_recovery
## Бот восстановления телеграм сообщений
Ваши сообщения теперь не пропадут, а отправятся Вам, если собеседник их удалит
Подлежат восстановлению: текст, фото, видео, аудиосообщения и другие файлы.

# Настройка (простой вариант)
Запускаем телеграм бота https://t.me/tg_recovery_bot и следуем его инструкции.
После завершения настройки Вы будете получать оповещения в случае удаления сообщений.

Пример работы бота:

![screen](welcome.png "Title")

# Настройка (сложный вариант)

1. Клонируем репозиторий `git clone https://github.com/imf1ne/tg_recovery.git`

2. Меняем параметры в файле *recover/settings.yml*

    2.1. Создаем API приложение на сайте https://my.telegram.org/ и берем значения *api_id*, *api_hash* (подробности о том как создать API приложение в телеграм боте ...)

    2.2. Вводим id чата телеграм, куда будут приходить восстановленные сообщения (желательно Избранные или там, где никто не увидит сообщения)

    2.3. Вводим свой часой пояс в формате для pytz (Пример: *"Europe/Moscow"*)


# Run

python3 recover.py

После авторизации будет создан файл `Secret@Name$Session.session`
