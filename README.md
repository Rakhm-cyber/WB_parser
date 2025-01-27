## Конфигурация окружения

Для корректной работы приложения создайте файл `.env` в корневой директории проекта со следующим содержимым:

```ini
POSTGRES_PASSWORD=(ваш пароль)
POSTGRES_USER=postgres
POSTGRES_DB=(название бд)
POSTGRES_HOST=(хост)
POSTGRES_PORT=5432
TG_TOKEN=(Токен вашего бота)
SECRET_TOKEN=Ваш секретный ключ
