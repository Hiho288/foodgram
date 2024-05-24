#  Foodgram


## О проекте

Проект для любителей не только вкусно поесть но и узнать новые рецепты блюд, где каждый зарегистрированный пользователь может не только поделиться фото своего завтрака обеда или ужина, но и написать его рецепт.

## Установка проекта

1. Клонируйте репозиторий
```bash
  git clone git@github.com:hiho288/foodgram-project-react.git
```
2. Установите переменные среды (какие именно - ниже. без них проект не запустится)
```bash
  nano .env
```
3. Установите Docker Compose поверх Docker'а
```bash
  sudo apt update && sudo apt-get install docker-compose-plugin
```
4. Запустите сборку из docker-compose файла
```bash
  sudo docker compose up -d
  # После запуска уйдет в фоновый режим. Для отображения логов уберите -d
```
## Что нужно указать в файле .env

```nano
POSTGRES_DB  - имя базы данных Postgresql
POSTGRES_USER  - имя пользователя с доступом к БД
POSTGRES_PASSWORD  - пароль для доступа к БД
DB_HOST  - адрес размещения БД (def.: контейнер db)
DB_PORT  - порт, по которому подключаться к БД (def.: 5432)

SETTINGS_SECRET_KEY  - ключ для django-проекта
SETTINGS_ALLOWED_HOSTS  - список адресов, с которых django-проект будет принимать запросы
SETTINGS_DEBUG - по умолчанию стоит False, но вписав любую переменную устанавливается True

```
