# Booking Hotels API

Бэкенд сервиса бронирования отелей: отели, номера, удобства, регистрация пользователей и бронирование номеров на даты с проверкой свободных мест.

**Стек:** FastAPI (async) · PostgreSQL + SQLAlchemy 2 (asyncpg) · Alembic · Redis (кеш + брокер) · Celery (worker + beat) · JWT в cookie · Nginx · uv · pytest · ruff · pyright · Docker Compose · GitLab CI/CD.

## Возможности

- **Отели и номера.** CRUD, поиск отелей по названию и локации с пагинацией.
- **Свободные номера на даты.** Отели и номера фильтруются по `date_from` / `date_to`: в выдачу попадает только то, где остались свободные номера на этот период.
- **Бронирование.** Перед созданием проверяется, что номер не занят полностью; цена берётся из номера.
- **Удобства** (Wi-Fi, кондиционер и т. п.) привязываются к номерам по схеме «многие ко многим».
- **Аутентификация.** Регистрация, вход, JWT в cookie `access_token`, пароли хранятся в bcrypt.
- **Кеширование** списков отелей и удобств в Redis на 10 секунд (`fastapi-cache2`).
- **Фоновые задачи.** Celery beat по расписанию запускает задачу, которая выбирает бронирования с заездом сегодня.
- **Nginx** перед приложением, с ограничением частоты запросов: 3 запроса в секунду с одного IP (`burst` 10), при превышении отвечает `429`.
- **CI/CD** в GitLab: линтеры, проверка типов, тесты, миграции и деплой через `docker compose`.

## API

Интерактивная документация после запуска: http://localhost/docs (через nginx).

Ручки с замком 🔒 требуют cookie `access_token`, которую ставит `POST /auth/login`. Swagger UI подставляет её сам после входа.

| Метод    | Путь                                  | Описание |
|----------|---------------------------------------|----------|
| `POST`   | `/auth/register`                      | Регистрация по email и паролю. `409`, если email уже занят |
| `POST`   | `/auth/login`                         | Вход: ставит cookie `access_token`. `401`, если email не найден или пароль неверный |
| `GET`    | `/auth/me` 🔒                         | Текущий пользователь |
| `POST`   | `/auth/logout`                        | Удаляет cookie |
| `GET`    | `/hotels?date_from=...&date_to=...`   | Отели со свободными номерами на даты. Фильтры: `title`, `location`; пагинация: `page`, `per_page`. Кешируется на 10 с |
| `GET`    | `/hotels/{hotel_id}`                  | Отель по id. `404`, если не найден |
| `POST`   | `/hotels`                             | Создать отель |
| `PUT`    | `/hotels/{hotel_id}`                  | Полностью обновить отель |
| `PATCH`  | `/hotels/{hotel_id}`                  | Частично обновить отель |
| `DELETE` | `/hotels/{hotel_id}`                  | Удалить отель |
| `GET`    | `/hotels/{hotel_id}/rooms?date_from=...&date_to=...` | Свободные номера отеля на даты, вместе с удобствами |
| `GET`    | `/hotels/{hotel_id}/rooms/{room_id}`  | Номер по id |
| `POST`   | `/hotels/{hotel_id}/rooms`            | Создать номер. `404`, если отеля нет |
| `PUT`    | `/hotels/{hotel_id}/rooms/{room_id}`  | Полностью обновить номер |
| `PATCH`  | `/hotels/{hotel_id}/rooms/{room_id}`  | Частично обновить номер |
| `DELETE` | `/hotels/{hotel_id}/rooms/{room_id}`  | Удалить номер |
| `GET`    | `/facilities`                         | Список удобств. Кешируется на 10 с |
| `POST`   | `/facilities`                         | Добавить удобство |
| `GET`    | `/bookings`                           | Все бронирования |
| `GET`    | `/bookings/me` 🔒                     | Бронирования текущего пользователя |
| `POST`   | `/bookings` 🔒                        | Забронировать номер. `409`, если свободных номеров нет; `404`, если номера нет |

Даты везде проверяются: если `date_from` позже `date_to`, ответ будет `422`. `per_page` принимает значения от 1 до 20.

Пример:

```bash
# регистрация и вход (cookie сохраняется в файл)
curl -X POST http://localhost/auth/register -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}'
curl -X POST http://localhost/auth/login -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}' -c cookies.txt

# свободные отели в Сочи на даты
curl "http://localhost/hotels?location=Сочи&date_from=2026-12-01&date_to=2026-12-10"

# бронирование
curl -X POST http://localhost/bookings -b cookies.txt -H "Content-Type: application/json" \
  -d '{"room_id": 1, "date_from": "2026-12-01", "date_to": "2026-12-10"}'
```

## Быстрый старт (Docker)

1. Склонируйте репозиторий и перейдите в него:

   ```bash
   git clone https://github.com/YazevStas/booking_hotels.git
   cd booking_hotels
   ```

2. Создайте `.env` из шаблона и подставьте свои значения:

   ```bash
   cp .env.example .env
   ```

   Внутри compose хосты — это имена сервисов: `DB_HOST=booking_db`, `DB_PORT=5432`, `REDIS_HOST=booking_cashe`, `REDIS_PORT=6379`. `DB_PASS` не может быть пустым, иначе Postgres не запустится. JWT-ключ можно сгенерировать командой `openssl rand -hex 32`.

3. Поднимите сервисы:

   ```bash
   docker compose up -d --build
   ```

   Compose сам выдерживает порядок запуска: Postgres (ждёт healthcheck) → миграции `alembic upgrade head` → бэкенд, Celery worker и beat → nginx.

4. Откройте http://localhost/docs.

5. Логи:

   ```bash
   docker compose logs -f                   # все сервисы
   docker logs -f booking_back              # один контейнер
   ```

Порты на хосте:

| Сервис     | Порт на хосте | Зачем |
|------------|---------------|-------|
| nginx      | `80`          | вход в API |
| PostgreSQL | `6432`        | подключиться DB-клиентом (`localhost:6432`) |
| Redis      | `7379`        | отладка |

У бэкенда порт наружу не проброшен, запросы к нему идут только через nginx.

## Тесты

Интеграционные тесты работают с настоящими PostgreSQL и Redis. Нужна **отдельная** база: перед запуском тесты удаляют и заново создают все таблицы, затем заполняют их данными из `tests/mock_hotels.json` и `tests/mock_rooms.json`.

```bash
cp .env-test.example .env-test   # MODE=TEST обязательно, DB_NAME — тестовая база
uv run pytest
```

Настройки берутся из `.env-test` (через `pytest-dotenv`, см. `pytest.ini`). Защита от случайного запуска на рабочей базе: если в настройках не `MODE=TEST`, тесты сразу падают.

```
tests/
  unit_tests/          # JWT: создание токена
  integration_tests/   # API через httpx AsyncClient + работа репозиториев с БД
  conftest.py          # пересоздание схемы, моки, авторизованный клиент
```

Линтеры и типы (те же проверки гоняет CI):

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pyright
```

## Конфигурация

Все настройки задаются переменными окружения, которые читает `src/config.py` (pydantic-settings):

```
.env  ──►  docker-compose.yml (env_file / ${VAR})  ──►  контейнеры  ──►  Settings
```

- `.env` и `.env-test` хранят реальные значения, лежат только локально и в git не попадают (`.gitignore`).
- `.env.example` и `.env-test.example` содержат тот же набор переменных без значений и коммитятся как шаблоны.

| Переменная                    | Описание |
|-------------------------------|----------|
| `MODE`                        | `LOCAL`, `DEV`, `PROD` или `TEST` (тесты запускаются только с `TEST`) |
| `DB_HOST`                     | хост Postgres (`booking_db` в compose, `localhost` без Docker) |
| `DB_PORT`                     | порт Postgres (`5432` внутри сети compose) |
| `DB_USER` / `DB_PASS`         | пользователь и пароль Postgres |
| `DB_NAME`                     | имя базы |
| `REDIS_HOST` / `REDIS_PORT`   | Redis для кеша и брокера Celery (`booking_cashe:6379` в compose) |
| `JWT_SECRET_KEY`              | секрет для подписи токенов |
| `JWT_ALGORITHM`               | алгоритм подписи, например `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | время жизни токена в минутах |

> Пользователь и пароль Postgres применяются только при **первой** инициализации тома `pg_data`. Если потом поменять `DB_PASS`, у самой базы останется старый пароль. Варианты: сменить пароль внутри базы (`ALTER USER ... PASSWORD '...'`) или пересоздать том (`docker compose down -v`, данные будут удалены).

## CI/CD

Пайплайн описан в `.gitlab-ci.yml`. Раннер работает с `docker`-executor и пробрасывает `/var/run/docker.sock`, поэтому job'ы управляют Docker'ом хоста, на котором запущен раннер.

| Стадия        | Job'ы                                   | Что делает |
|---------------|-----------------------------------------|------------|
| `build`       | `build`                                 | Собирает образ; в `main` пушит его в GitLab Container Registry с тегами `<sha>` и `latest` |
| `lint_format` | `ruff_check`, `ruff_format`, `pyright`  | Линтер, проверка форматирования, проверка типов |
| `migrations`  | `migrations`                            | Только `main`: поднимает БД и применяет миграции на проде |
| `test`        | `test`                                  | `pytest` с одноразовыми Postgres и Redis (`services:` GitLab) |
| `deploy`      | `deploy`                                | Только `main`: `docker compose up -d --build --remove-orphans` |

Python-job'ы используют общий шаблон `.python` (образ `python:3.14-slim`, `uv sync --frozen`, кеш uv по `uv.lock`). Job'ы прода используют шаблон `.compose`: образ `docker`, правило «только main», `.env` из переменной CI.

Переменные CI/CD (**Settings → CI/CD → Variables**, тип **File**):

| Переменная | Содержимое |
|------------|------------|
| `ENV_PROD` | `.env` для прода (формат как в `.env.example`) |
| `ENV_TEST` | `.env-test` для тестов: `DB_HOST=postgres`, `REDIS_HOST=redis`, учётные данные как у `POSTGRES_*` в job'е `test` |

Прод-стек запускается под именем проекта compose `booking_prod`, поэтому его volume не пересекаются с локальным запуском. Управлять им вручную:

```bash
docker compose -p booking_prod ps
docker compose -p booking_prod logs -f booking_back
docker compose -p booking_prod start     # поднять после перезагрузки
```

## Устройство

Слоистая архитектура: **API → сервисы → репозитории → ORM**. Слои общаются через pydantic-схемы, ORM-объекты наружу из репозиториев не выходят.

```
src/
  main.py            # приложение FastAPI, lifespan: подключение Redis и кеша
  config.py          # Settings (pydantic-settings)
  database.py        # движок и фабрики сессий (обычная и NullPool для тестов/Celery)
  exception.py       # доменные исключения и их HTTP-версии
  api/               # роутеры и зависимости (DBDep, UserIdDep, PaginationDep)
  services/          # бизнес-логика; TokenService — JWT, AuthService — пользователи
  repositories/      # доступ к данным; mappers/ — ORM ↔ pydantic, utils.py — запрос свободных номеров
  models/            # ORM-модели: hotels, rooms, facilities, rooms_facilities, bookings, users
  schemas/           # pydantic-схемы запросов и ответов
  utils/db_manager.py  # Unit of Work: одна сессия и все репозитории на запрос
  connectors/        # обёртка над Redis
  tasks/             # Celery: приложение, расписание beat, задачи
  migrations/        # Alembic
tests/               # unit и integration тесты
Dockerfile           # образ приложения (uv, без dev-зависимостей)
nginx.Dockerfile     # образ nginx с nginx.conf внутри
nginx.conf           # прокси на booking_back:8000 + rate limit
docker-compose.yml   # БД, Redis, миграции, бэкенд, nginx, Celery
.gitlab-ci.yml       # CI/CD
```

Решения:

- **Unit of Work.** `DBManager` открывает одну сессию на запрос, даёт доступ ко всем репозиториям (`db.hotels`, `db.rooms` и т. д.) и коммитит явно через `db.commit()`. Поэтому изменения в нескольких таблицах попадают в одну транзакцию.
- **Свободные номера.** Один SQL-запрос с CTE (`repositories/utils.py`): считает бронирования номера, которые пересекаются с периодом, вычитает их из `quantity` и оставляет номера с `rooms_left > 0`. Этот же запрос используется для фильтра отелей и для проверки перед бронированием.
- **Миграции отдельным контейнером.** `booking_migrations` применяет `alembic upgrade head` и завершается. Бэкенд и worker стартуют только после его успешного завершения (`service_completed_successfully`), поэтому приложение никогда не работает со старой схемой.
- **Конфиг nginx внутри образа**, а не через volume. При запуске из CI через `docker.sock` bind mount ищет файл на диске хоста, а не в контейнере job'а, поэтому конфиг копируется на этапе сборки (`nginx.Dockerfile`).
- **NullPool для тестов и Celery.** Каждая задача Celery вызывает `asyncio.run` и создаёт новый event loop, а соединения из пула привязаны к старому. NullPool открывает соединение заново на каждую сессию.

## TODO

- [ ] Добавить `packaging` в зависимости: без него Celery worker и beat не запускаются в прод-образе (`ModuleNotFoundError`)
- [ ] Реализовать отправку писем в задаче `booking_today_checkin` (сейчас она только выбирает бронирования и пишет их в лог)
- [ ] Защитить авторизацией изменение отелей, номеров и удобств
- [ ] Перенести стадию `migrations` после `test`, чтобы миграции на проде применялись только после прохождения тестов
- [ ] Добавить `restart: unless-stopped` сервисам, чтобы прод-стек поднимался после перезагрузки
- [ ] Health-check эндпоинт
