# HH Analytics — план проекта

Консольная утилита: собирает вакансии с hh.ru по запросу, сохраняет в SQLite и строит аналитику (зарплаты, навыки, работодатели, города).

```bash
python -m hh_parser collect "python" --area 1 --pages 10   # собрать вакансии
python -m hh_parser details --async                       # дособрать навыки (асинхронно)
python -m hh_parser stats "python"                        # таблица статистики
python -m hh_parser plot salaries --query python          # график
```

## Темы → где в проекте

| Тема | Где |
|---|---|
| requests | `clients/sync_client.py` — Session, заголовки, повторы, паузы |
| ООП | модели (dataclass), `BaseClient` → два клиента, парсеры, репозиторий, сервис |
| Несколько файлов | пакет `hh_parser/` с подпакетами |
| CLI | `cli.py` — argparse, подкоманды |
| БД + SQL | `storage/` — схема, upsert, many-to-many; `analytics/queries.py` |
| async | `clients/async_client.py` — aiohttp + Semaphore |
| Визуализация | `analytics/plots.py` — matplotlib |

## Структура

```
hh-analytics/
├── README.md
├── PLAN.md
├── requirements.txt
├── .gitignore                  # .venv/, data/, __pycache__/
├── data/                       # (в .gitignore) hh.db, графики
├── prototype.py                # текущий main.py — как шпаргалка, потом удалить
│
├── hh_parser/
│   ├── __init__.py
│   ├── __main__.py             # точка входа: python -m hh_parser
│   ├── cli.py
│   ├── config.py               # URL, заголовки, пути, задержки, лимиты
│   ├── models.py               # Vacancy, Salary, Employer
│   ├── clients/
│   │   ├── base.py             # абстрактный BaseClient
│   │   ├── sync_client.py      # HHClient (requests)
│   │   └── async_client.py     # AsyncHHClient (aiohttp)
│   ├── parsers/
│   │   ├── search_page.py      # HTML выдачи → list[Vacancy]
│   │   ├── vacancy_page.py     # HTML вакансии → навыки, опыт
│   │   └── salary.py           # строка → Salary
│   ├── storage/
│   │   ├── schema.sql
│   │   ├── db.py
│   │   └── repository.py
│   ├── analytics/
│   │   ├── queries.py
│   │   └── plots.py
│   └── services/
│       └── collector.py        # клиент + парсер + репозиторий
│
└── tests/
    ├── fixtures/               # сохранённые HTML-страницы
    ├── test_salary.py
    ├── test_parsers.py
    └── test_repository.py
```

## Схема БД

```
searches        (id, query, area, started_at, found_total)
employers       (id, name)
vacancies       (id, title, employer_id → employers, area,
                 salary_from, salary_to, currency, experience,
                 url, published_at, collected_at, details_loaded)
search_vacancy  (search_id → searches, vacancy_id → vacancies)
skills          (id, name UNIQUE)
vacancy_skills  (vacancy_id → vacancies, skill_id → skills)
```

---

## Общие правила работы

- **Маленькие шаги.** Написал кусок → запустил → работает → коммит. Не пиши 300 строк, чтобы потом их отлаживать.
- **Один этап = одна ветка или хотя бы серия коммитов** с понятными сообщениями (`feat: salary parser`, `fix: ...`).
- **Сначала «как вызывать», потом «как реализовать».** Перед классом напиши, как будешь его использовать:
  `client = HHClient(); html = client.get_search_page("python", page=0)`. Если вызов выглядит неудобно — меняй дизайн до кода.
- **Не ходи в интернет без нужды.** Сохранил страницу один раз → дальше отлаживай парсер на файле. Быстрее и не забанят.
- **`print` → `logging`** с этапа 2.
- **Застрял больше чем на 30 минут** — сформулируй вопрос письменно (что хочу, что делаю, что получаю). Половина проблем решается на этом шаге.

---

## Этап 0. Подготовка (½ дня)

- [ ] `git init`, `.gitignore` (`.venv/`, `data/`, `__pycache__/`, `*.db`)
- [ ] `requirements.txt`: requests, beautifulsoup4, aiohttp, matplotlib, pytest
- [ ] `main.py` → `prototype.py` (шпаргалка), `response.html` → `tests/fixtures/search_page.html`
- [ ] Каркас пакета: пустые файлы + `__init__.py`
- [ ] `__main__.py` печатает «hello», запуск `python -m hh_parser`

**Как подходить**
- Разберись, чем `python -m hh_parser` отличается от `python hh_parser/cli.py` — это про то, как Python ищет модули, и от этого зависят импорты во всём проекте.
- Используй абсолютные импорты: `from hh_parser.models import Vacancy`.
- Проверь себя: почему `__init__.py` нужен и что будет без него?

✅ Пакет запускается как модуль, первый коммит сделан.

---

## Этап 1. Модели и ООП-основа (1 день)

- [ ] `Salary` (`from_`, `to`, `currency`, `gross`) — `@dataclass(frozen=True)`
- [ ] Свойство `Salary.avg`, метод `__str__`
- [ ] `Vacancy` (`id`, `title`, `employer`, `area`, `salary`, `url`, `skills: list[str]`)
- [ ] `parsers/salary.py`: `parse_salary(text: str) -> Salary | None`
- [ ] Тесты на парсер зарплаты

**Как подходить**
- **Начни с тестов для зарплаты.** Выпиши из `response.html` 8–10 реальных вариантов строк («от 100 000 ₽», «до 2 000 $», «100 000 – 150 000 ₽ за месяц, на руки», пустая строка) — каждый станет тестом. Потом пиши функцию, пока все не позеленеют. Это самое честное знакомство с TDD.
- Внимание: в строках hh неразрывные пробелы `\xa0` и узкие ` ` — первая ловушка.
- `frozen=True` — чтобы объект нельзя было случайно изменить. Подумай, почему для `Salary` это уместно, а для `Vacancy` (у которой потом дозаполняются навыки) — может быть, нет.
- Для `skills` используй `field(default_factory=list)` — и выясни, почему нельзя `skills: list = []`.
- Модели — это **только данные**. Никаких запросов и SQL внутри `Vacancy`.

✅ `pytest` зелёный, все реальные форматы зарплат разбираются.

---

## Этап 2. requests: синхронный клиент (1 день)

- [ ] `config.py`: `BASE_URL`, `HEADERS`, `REQUEST_DELAY`, `MAX_RETRIES`
- [ ] `clients/base.py`: абстрактный `BaseClient` (`abc.ABC`, `@abstractmethod`)
- [ ] `HHClient(BaseClient)`: `requests.Session`, `get_search_page(query, page, area=None)`, `get_vacancy_page(vacancy_id)`
- [ ] Пауза между запросами, повтор при 403/429/5xx, `timeout=` в каждом запросе
- [ ] `logging` вместо `print`
- [ ] Сохранить в `tests/fixtures/` 1–2 страницы вакансий

**Как подходить**
- Клиент **возвращает HTML-строку** и ничего не знает о BeautifulSoup. Скачивание и разбор — разные обязанности (принцип единственной ответственности).
- `Session` переиспользует соединение и cookies — сравни время 10 запросов через `requests.get` и через `session.get`.
- Повторы: напиши сначала простой цикл `for attempt in range(MAX_RETRIES)` с растущей паузой (1, 2, 4 сек). Потом можно узнать про `urllib3.Retry` — но свой цикл полезнее для понимания.
- Сделай клиент контекстным менеджером (`__enter__`/`__exit__` закрывают сессию) — хорошая ООП-практика.
- `r.raise_for_status()` и свои исключения (`class HHBlockedError(Exception)`) — чтобы верхний код мог понять, что именно пошло не так.

✅ `HHClient().get_search_page("техник", 0)` возвращает HTML, в логах видны запросы и паузы.

---

## Этап 3. Парсеры (1–2 дня)

- [ ] `SearchPageParser.parse(html) -> list[Vacancy]`
- [ ] Отдельно: `parse_total_found(html) -> int` («Найдено 275 065 вакансий»)
- [ ] `VacancyPageParser.parse(html) -> dict` (навыки, опыт)
- [ ] Тесты на фикстурах — без интернета

**Как подходить**
- Работай в паре «DevTools в браузере + фикстура». Нашёл элемент → проверил селектор в `python -i` на файле → перенёс в код.
- Опирайся на `data-qa`, не на классы вроде `vacancy-info--ieHKDTkezpEj0Gsx` — они меняются при каждом деплое hh.
- Разбирай **по карточкам**: сначала найди все карточки вакансий, потом внутри каждой ищи название, зарплату и т. д. Иначе списки разъедутся (у одной вакансии нет зарплаты — и все зарплаты сдвинутся).
- `id` вакансии бери из ссылки (`/vacancy/123456789`) — это будет первичный ключ в БД.
- Отсутствующий элемент — норма, а не ошибка: `el.get_text() if el else None`.
- Тест: «на фикстуре ровно 20 вакансий, у первой такой-то title, у всех есть id и url».

✅ Из фикстуры получается 20 корректных `Vacancy`, тесты зелёные.

---

## Этап 4. БД и SQL (2 дня)

- [ ] `schema.sql` (таблицы выше), `PRAGMA foreign_keys = ON`, индексы на `vacancies(area)`, `vacancy_skills(skill_id)`
- [ ] `db.py`: `get_connection(path)`, `init_db(conn)` (выполняет `schema.sql`)
- [ ] `VacancyRepository(conn)`: `save_search()`, `save_vacancies()`, `save_skills(vacancy_id, skills)`, `get_without_details(limit)`
- [ ] `services/collector.py`: `Collector(client, parser, repo).collect(query, pages, area)`
- [ ] Тесты репозитория на `sqlite3.connect(":memory:")`

**Как подходить**
- **Сначала SQL руками.** Открой `sqlite3 data/hh.db` (или DB Browser for SQLite), создай таблицы, вставь пару строк, сделай JOIN. Только когда запросы работают в консоли — переноси в Python.
- Только параметры `?`: `conn.execute("... WHERE id = ?", (vid,))`. Никогда f-строки — разберись, что такое SQL-инъекция.
- Upsert: `INSERT INTO ... ON CONFLICT(id) DO UPDATE SET ...` — одна вакансия найдётся по разным запросам, дубликатов быть не должно.
- Навыки (many-to-many): `INSERT OR IGNORE INTO skills(name)`, потом `SELECT id`, потом связь. Подумай, как сделать это за минимум запросов.
- `executemany` и транзакции: вставка 50 строк по одной с `commit()` после каждой vs. одна транзакция — замерь разницу.
- `conn.row_factory = sqlite3.Row` — удобный доступ к колонкам по имени.
- Репозиторий **принимает соединение снаружи** (а не создаёт сам) — тогда в тестах легко подсунуть `:memory:`. Это dependency injection.
- `Collector` тоже получает клиент/парсер/репозиторий в конструкторе — так на этапе 6 подменишь клиент на асинхронный без переписывания.

✅ После сбора в `data/hh.db` есть вакансии, повторный сбор не плодит дубли.

---

## Этап 5. CLI (1 день)

- [ ] `cli.py`: `argparse` с `add_subparsers`: `collect`, `details`, `stats`, `plot`
- [ ] `collect QUERY [--area] [--pages] [--per-page]`
- [ ] Общие флаги: `--db PATH`, `-v/--verbose`
- [ ] Понятные ошибки, `sys.exit(1)` при сбое
- [ ] `__main__.py` вызывает `cli.main()`

**Как подходить**
- Сначала напиши в README, **как ты хочешь вызывать** команды. Потом реализуй ровно это.
- Каждая подкоманда — отдельная функция `cmd_collect(args)`; связывай через `parser.set_defaults(func=cmd_collect)`.
- `main(argv=None)` принимает список аргументов — тогда CLI можно тестировать: `main(["collect", "python", "--pages", "1"])`.
- `-v` переключает `logging.basicConfig(level=DEBUG/INFO)` — вот где окупится logging из этапа 2.
- Прогресс: простое `страница 3/10, сохранено 60` уже хорошо. Хочется красоты — библиотеки `tqdm` или `rich`.
- Как продвинутый шаг потом сравни argparse с `typer`/`click` — но учись на argparse, он в стандартной библиотеке.

✅ `python -m hh_parser collect "техник" --pages 3` наполняет БД; `--help` у каждой команды понятный.

---

## Этап 6. async (2 дня)

- [ ] `AsyncHHClient(BaseClient)` на `aiohttp.ClientSession`
- [ ] `asyncio.Semaphore(3)` + пауза внутри семафора
- [ ] Команда `details [--async] [--limit N]`: вакансии без навыков → скачать страницы → распарсить → сохранить
- [ ] Синхронная версия той же команды, замер времени обеих

**Как подходить**
- **Сначала разберись с asyncio отдельно**, вне проекта: скрипт с `async def`, `await asyncio.sleep(1)` и `asyncio.gather` на 10 задач. Пойми, почему 10 «снов» по секунде занимают 1 секунду, а не 10. Потом `aiohttp` на 5 любых URL.
- `async` полезен там, где много **независимых** запросов — страницы отдельных вакансий идеально подходят. Страницы поиска тоже можно, но там проще упереться в бан.
- Семафор — это «не больше N запросов одновременно». Без него `gather` на 500 задач = 500 одновременных запросов = мгновенный бан DDoS-Guard.
- Одна `ClientSession` на всё время работы (`async with`), не новая на каждый запрос.
- Не смешивай: внутри `async def` не вызывай `requests` и `time.sleep` — они блокируют весь цикл. Зато sqlite можно писать после `gather`, пачкой.
- `asyncio.gather(..., return_exceptions=True)` — чтобы одна упавшая вакансия не убила все остальные.
- Абстрактный базовый класс и асинхронность конфликтуют (методы `async def` vs обычные). Подумай, как это решить: два разных базовых класса? `Protocol`? Это хороший вопрос на подумать, а не ошибка в плане.
- Замер: `time.perf_counter()` до/после. Запиши результат в README.

✅ `details --async` заметно быстрее синхронной версии и не ловит 403.

---

## Этап 7. Аналитика на SQL (1–2 дня)

- [ ] Средняя и медианная зарплата по городам (`GROUP BY area HAVING COUNT(*) >= 10`)
- [ ] Зарплата по опыту
- [ ] Топ-20 навыков по запросу (JOIN `vacancies` × `search_vacancy` × `vacancy_skills` × `skills`)
- [ ] Топ работодателей по числу вакансий
- [ ] Топ-3 навыка для каждого запроса — `ROW_NUMBER() OVER (PARTITION BY ...)`
- [ ] Средняя зарплата с навыком X и без него (`CASE`, подзапрос или `EXISTS`)
- [ ] Команда `stats QUERY` выводит таблицы в терминал

**Как подходить**
- Каждый запрос **сначала в консоли sqlite**, потом в коде. Сложные строй по частям через CTE (`WITH ... AS (...)`).
- Зарплата: у вакансии может быть только `from` или только `to`. Реши осознанно, как считать «зарплату вакансии» (`COALESCE`, среднее из двух), и запиши решение в README.
- Валюты: либо фильтруй только `RUR`, либо конвертируй — но не смешивай рубли с долларами.
- В SQLite нет встроенной медианы — это хорошая задача: через оконные функции или посчитать в Python.
- Функции в `queries.py` возвращают данные (список строк), а не печатают — печатью занимается CLI, графиками — `plots.py`. Одни и те же данные пойдут в обе стороны.
- `EXPLAIN QUERY PLAN` — посмотри, используются ли твои индексы.

✅ `stats "python"` показывает осмысленные цифры, которые ты можешь объяснить.

---

## Этап 8. Визуализация (1 день)

- [ ] Гистограмма зарплат
- [ ] Горизонтальный bar-chart топ-20 навыков
- [ ] Boxplot «зарплата по опыту»
- [ ] Сравнение двух запросов на одном графике
- [ ] Команда `plot salaries|skills|experience --query ... [--save PATH]`

**Как подходить**
- Используй объектный API: `fig, ax = plt.subplots()` и `ax.hist(...)`, а не `plt.hist(...)` — так проще делать несколько графиков и тестировать.
- Функция графика принимает **данные**, а не соединение с БД: `plot_salaries(salaries: list[int], title: str) -> Figure`. Данные — из `queries.py`.
- Перед тем как рисовать, ответь: какой вопрос отвечает этот график? «Сколько платят python-разработчикам в Москве» → гистограмма; «что учить» → навыки.
- Обрежь выбросы (зарплаты в 10 млн) или используй перцентили — иначе гистограмма будет одним столбиком.
- Подписи осей, заголовок, форматирование тысяч (`120k` или `120 000`), `fig.tight_layout()`. Мелочи, но именно они отличают нормальный график.
- `--save` → `fig.savefig(path, dpi=150)`, без него → `plt.show()`.

✅ Каждый график строится одной командой из БД и понятен без пояснений.

---

## Этап 9. Доводка (1 день)

- [ ] README: что делает, установка, примеры команд, скриншоты графиков, замер sync vs async
- [ ] Аннотации типов везде, `ruff check` и `ruff format`
- [ ] Удалить `prototype.py`
- [ ] Перечитать весь код как чужой: что непонятно — переименовать или прокомментировать

**Как подходить**
- Склонируй репозиторий в чистую папку и пройди README с нуля. Всё, на чём споткнулся, — исправь.
- Ищи повторяющийся код — частый кандидат вынести в функцию или базовый класс.
- Код-ревью: попроси меня посмотреть (`/code-review`), но после того, как сам перечитал.

✅ Проект не стыдно положить в резюме.

---

## Если захочется больше

- `ApiClient` для `api.hh.ru` как третья реализация клиента, флаг `--source api|html`
- PostgreSQL вместо SQLite, `asyncpg`
- Дашборд на Streamlit поверх той же БД
- Docker + сбор по расписанию (cron)
- Сравнение навыков/зарплат во времени (повторные сборы раз в неделю)
