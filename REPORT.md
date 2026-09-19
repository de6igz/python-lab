# Отчёт: генераторы статических сайтов

Артём Солопов · Задание 1 · T2 и P3

Статус: локальная часть выполнена; публикация на хостингах и сдача в Moodle отложены.


---

# Отчёт по заданию 1

Автор: Артём Солопов. Выбраны T2 и P3. Основной стек: Python 3.12.13,
MkDocs 1.6.1, Material 9.6.14, стандартная библиотека Python для эксперимента.

## Статус

Локальная реализация собрана и проверена. Строгая сборка, тесты,
проверка кэша, обновление CSV/SVG и аудит локальных ссылок прошли успешно. Публикация в GitHub и на отечественном хостинге отложена
по решению автора; ссылки, remote run и скриншоты внешнего CI пока отсутствуют.

## Выполнение основного хода работы

| Пункты задания | Реализация |
| --- | --- |
| 1–3: Python, pip, virtualenv | Python 3.12.13; virtualenv 20.31.2; проверено отдельное окружение с pip 25.1.1 |
| 4: фиксация зависимостей | requirements.txt содержит точные версии всех установленных пакетов; .gitignore исключает кэши и сборки |
| 5–6: каркас и строгая сборка | Material for MkDocs; Makefile запускает эксперимент перед сборкой |
| 7–8: репозиторий и Actions | Локальный Git уже инициализирован; workflow подготовлен; удалённая публикация ожидает следующего этапа |
| 9–10: отечественный хостинг | Подготовлен SSH/rsync-скрипт и выключенная до настройки job |
| 11: базовый URL | SITE_URL для каждой площадки, относительные ссылки, use_directory_urls=false |
| 12: проверка результата | HTTP healthcheck, аудит локальных ссылок/ресурсов, поиск и нативная формула |
| 13: лицензии | MIT для кода, CC BY 4.0 для текста, CC0 для учебного CSV |
| 14: отладка | Три реально запускаемые отрицательные проверки и логи в evidence/ |

## Исследовательская и практическая части

[T2 — сравнение способов исполнения и публикации](docs/research.md) содержит матрицу,
ограничения CI и границу вынесения тяжёлых расчётов. [P3](docs/pipeline.md) реализует
генерацию CSV/SVG/Markdown, кэш по содержимому входов и метки версии.

## Отладка

Ниже — намеренно воспроизведённые ошибки, а не выдуманная история разработки.
Полные stdout/stderr сохранены в `evidence/failure-*.log`.

| Ошибка | Гипотеза | Проверка | Решение |
| --- | --- | --- | --- |
| `ValueError: workers/run must be positive; seconds must be finite and positive` | Во входе отрицательное время | Запуск скрипта с seconds=-1 | Отбраковка входа до расчёта; восстановление положительного времени |
| Strict build: ссылка на `absent.md` | Документ отсутствует | Отдельная тестовая сборка с битой ссылкой | Ссылка заменена на существующий заголовок |
| Strict build: якорь `#absent` | Несовпадение идентификатора раздела | Сборка с включённым validation.links.anchors=warn | Ссылка заменена на `#test`; повторная строгая сборка успешна |

Дополнительно проверяется повреждение кэшированного JSON: несовпадение хеша
приводит к пересчёту, а не публикации повреждённого результата.

## Вывод

Для небольших воспроизводимых CPU-экспериментов рекомендуется Python → CSV/SVG/Markdown
→ MkDocs Material → CI → статический хостинг. Это сокращает число зависимостей
и делает связь входов с результатом явной. Для книги со сложными перекрёстными
ссылками и ноутбуками предпочтительнее Sphinx/MyST-NB или Quarto; тяжёлые GPU-расчёты
нужно выполнять отдельно, публикуя проверяемые артефакты. Вывод относится к учебной
публикации; синтетические данные не дают научного вывода о реальном оборудовании.

## Измерения

Машина: macOS-26.6.2-arm64-arm-64bit, Python 3.12.13. Время — wall-clock через
`time.perf_counter`, включая запуск процесса. Пять парных запусков эксперимента
с пустым и заполненным кэшем; три независимых `mkdocs build --strict`.
Это локальные замеры, а не время GitHub runner.

| Показатель | Значение | Метод |
| --- | --- | --- |
| Расчёт без кэша, медиана | 0.373798 с | 5 запусков, удаление только тестового кэша |
| Расчёт с кэшем, медиана | 0.061771 с | 5 повторных запусков с теми же входами |
| Отношение медиан | 6.05 раза | без искусственных задержек |
| Строгая сборка MkDocs, медиана | 0.480051 с | 3 запуска, уже сгенерированные страницы |
| HTML страницы результатов | 18057 байт | без сжатия |
| Измеренная сборка целиком | 3001419 байт | со скриншотами; сумма файлов перед финальной редактурой отчёта |
| Удалённая доставка Pages / Helios | Не измерена | публикация отложена |

Исходные ряды: `evidence/measurements.csv`; сводка: `evidence/summary.json`.

## Изменение данных и кэш

В копии CSV изменено время для workers=8, run=1: 3.5 → 2.5 с. Среднее в группе
изменилось с 3.540 до 3.340 с; ключ кэша и SVG изменились. Повторный запуск с
неизменными входами использует кэш. Повреждённый JSON пересчитывается. Подробности
до/после сохранены в `evidence/data-change.json`. Оригинал набора не изменён.

## Проверки в браузере

| Проверка | Наблюдение |
| --- | --- |
| Главная страница | Контрольная строка присутствует |
| Страница результатов | Формула, четыре столбца графика и таблица отображаются |
| Русскоязычный поиск | Запрос «вычисления» возвращает два совпадения в первой проверенной сборке |
| Внешние ресурсы HTML/CSS | Аудит не обнаружил CDN и отсутствующих локальных ссылок |

Скриншот сохранён в локальном архиве; публичная загрузка ожидает подтверждения.

Скриншот сохранён в локальном архиве; публичная загрузка ожидает подтверждения.

Скриншоты относятся к локальному предпросмотру, не к удалённому CI.

## Проверка без внешних CDN и в подкаталоге

Итоговая сборка обслуживалась по `/site/` локальным сервером с CSP, разрешающим
ресурсы только с того же origin. Фактический заголовок и HTTP 200 с контрольной
строкой сохранены в `evidence/http-csp.json`. В этой конфигурации формула и график
отображаются, поиск «вычисления» возвращает три страницы (в индекс вошёл отчёт).
В консоли браузера предупреждений и ошибок не обнаружено.

![График в подкаталоге, внешние ресурсы заблокированы](docs/assets/evidence/chart-offline.png)

Скриншот сохранён в локальном архиве; публичная загрузка ожидает подтверждения.

Для формул дополнительные JS-ресурсы не загружаются: нативный MathML добавляет
только разметку в HTML. Подключение собственного MathJax здесь не требуется.

## Учебные материалы

Прочитаны условие задания и раздел «Практика 1» курса, в том числе описание
`public_html` и URL пользовательского сайта Helios. Ссылка на Яндекс Диск ведёт
к видео «0. Публикация на GitHub Pages на основе Hugo + Jekyll.webm».
Видеоматериал не использовался как доказательство выполненных действий;
реализация и исследование опираются на ТЗ, фактические проверки и официальную
документацию, указанную в T2.


---

# T2. Эксперимент → артефакт → страница

## Сравнение стратегий

| Способ | Что выполняется при сборке | Кэш и параметры | Сильная сторона | Риск и цена поддержки |
| --- | --- | --- | --- | --- |
| Изображения, сохранённые вручную | SSG копирует PNG/SVG | Внешняя организация, параметры нужно записать отдельно | Минимум зависимостей, быстрый просмотр | График может перестать соответствовать данным; ручные действия трудно повторить |
| nbconvert | `jupyter nbconvert --to notebook --execute input.ipynb` выполняет ячейки; затем экспорт | Сам по себе не полноценный кэш результатов; нужен внешний ключ и хранилище | Простой переход от ноутбука к автоматизации | Состояние ядра, время исполнения, относительные пути; по умолчанию ошибка ячейки прерывает запуск |
| MyST-NB | Sphinx исполняет ноутбук и встраивает вывод | `nb_execution_mode = "cache"`, jupyter-cache | Текст, код и результат рядом; научные ссылки Sphinx | Изменение внешнего CSV само по себе не гарантирует сброс кэша; окружение и входы надо учитывать дополнительно |
| Quarto | Исполнение Jupyter/knitr при render | `cache: true`, `freeze: auto/true`, параметры документа | Единый источник HTML/PDF и вычислительных публикаций | `freeze` действует при общей сборке; для `.ipynb` выполнение по умолчанию выключено. Изменение данных требует обновления кэша |
| papermill | Исполнение шаблонного ноутбука с параметрами | `-p` или YAML `-f`; кэш организует оркестратор | Серии экспериментов и сохранённый выходной ноутбук на каждый набор параметров | Не является генератором сайта; нужен экспорт, реестр запусков и проверка зависимостей |
| Python → Markdown/CSV через Make | Скрипт считает, SSG только оформляет | Явный ключ из кода, данных, версий и параметров | Прозрачные артефакты; тестируемая граница вычислений | Самостоятельно поддерживаются кэш, подписи, метаданные и формат страниц |

Для P3 выбран последний вариант: небольшой детерминированный bootstrap-расчёт,
один CSV, возможность проверить весь путь без ядра Jupyter. MkDocs выбран как
генератор на Python с простым Markdown, локальным поиском и строгой сборкой.
Это выбор для данной задачи, а не результат сравнительного исследования T1.

## Ограничения CI

По официальной документации GitHub Actions, проверенной 19.09.2026:

| Ограничение | Значение / условие | Практическое следствие |
| --- | --- | --- |
| Время одной job на GitHub-hosted runner | До 6 часов | Длительный эксперимент может быть прерван; в этой работе timeout 10 минут |
| Время self-hosted job | До 5 суток | Собственный раннер не означает отсутствие лимитов |
| GitHub Free: включённые минуты | 2000 минут/месяц для тарифицируемого использования | Нельзя считать бюджет вычислений неограниченным; публичные репозитории со стандартными раннерами имеют отдельные условия бесплатного использования |
| Хранение artifacts, Free | 500 MB по таблице тарифных лимитов | Хранить небольшой сайт, а не все промежуточные массивы; срок хранения ограничить |
| Кэш, базовый объём на репозиторий | 10 GB | Кэш может быть вытеснен; отсутствие кэша не должно менять правильность результата |
| GPU стандартного раннера | Не предоставляется | GPU-обучение переносится на отдельную инфраструктуру; larger/self-hosted раннеры требуют отдельного выбора и бюджета |
| Размер артефакта | Зависит от API, квоты, типа публикации | Квота 500 MB не равна универсальному пределу одного файла; проверять также лимит GitHub Pages и доступное место |

Лимиты меняются, тариф и платформа проверяются перед публикацией. В GitVerse,
SourceCraft и других CI действуют собственные квоты, переносить числа GitHub нельзя.
В расчёт бюджета входят скачивание данных, установка окружения, сам эксперимент,
рендеринг и доставка; кэш ускоряет типичный запуск, но не гарантируется.

## Где провести границу

В CI допустим расчёт, если он детерминирован, не требует закрытых данных и GPU,
стабильно укладывается в короткий timeout и доступную память даже без кэша.
Для этой работы bootstrap по 20 наблюдениям подходит; полноценное обучение модели
на GPU или многочасовой численный эксперимент — нет.

Для тяжёлого эксперимента отдельный вычислительный запуск публикует неизменяемый
набор артефактов. CI получает именно его версию, проверяет SHA-256 и строит сайт.
Минимальный манифест содержит:

```json
{
  "run_id": "experiment-2026-09-19-001",
  "code_commit": "полный SHA коммита",
  "dataset_version": "версия и SHA-256 данных",
  "environment": "хеш lock-файла или digest контейнера",
  "parameters": {"seed": 3960, "replicates": 20000},
  "artifacts": {"summary.csv": "SHA-256", "chart.svg": "SHA-256"}
}
```

Манифест здесь — пример схемы, не свидетельство выполненного внешнего запуска.
На сайте P3 публикуется фактический `metadata.json`. Коммит идентифицирует код,
SHA-256 — конкретные байты данных; дата сборки не заменяет ни один из них.
Если есть незакоммиченные изменения, это явно отмечается. Контрольная сумма
обнаруживает случайную порчу, но сама по себе не удостоверяет автора:
для недоверенного хранилища нужна проверенная подпись манифеста.

## Источники

1. [nbconvert: Executing notebooks](https://nbconvert.readthedocs.io/en/latest/execute_api.html).
2. [MyST-NB: Execute and cache](https://myst-nb.readthedocs.io/en/latest/computation/execute.html).
3. [Quarto: Managing Execution](https://quarto.org/docs/projects/code-execution.html).
4. [papermill: Execute](https://papermill.readthedocs.io/en/latest/usage-execute.html).
5. [GitHub Actions: Limits](https://docs.github.com/en/actions/reference/limits).

Сравнение сделано по документации, а не по замерам скорости этих пяти инструментов.


---

# P3. Воспроизводимый конвейер

## Запуск с чистого окружения

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
make test
make build
make serve
```

Версия Python зафиксирована в `.python-version` (3.12.13), прямые и транзитивные
зависимости — в `requirements.txt`. Для выполнения исходного пункта о virtualenv:
`python -m virtualenv .work/virtualenv-check`; основной проект тоже можно создать
через virtualenv вместо venv. Необходимые внешние программы: Git и Make;
для доставки — OpenSSH и rsync. На чистом раннере зависимости устанавливает workflow.

## Поток данных

```text
data/timings.csv + scripts/experiment.py + requirements.txt + Python + seed
                         ↓ SHA-256
                 проверка кэша результата
                         ↓
        summary.csv + chart.svg + metadata.json + results.md
                         ↓
                  mkdocs build --strict
                         ↓
             HTML, локальный поиск, CSS/JS
                         ↓
          Pages / SSH-хостинг → HTTP healthcheck
```

Кэш сохраняет только вычислительные результаты. Метаданные сборки и страницы
создаются заново даже при попадании в кэш: иначе на странице остался бы старый коммит.
Ключ включает полный хеш CSV, скрипта, requirements, версию Python и параметры.
Перед чтением проверяется хеш самого кэшированного JSON. Изменение или порча входов
заставляет выполнить расчёт; потеря кэша влияет только на скорость.

## Демонстрация обновления

Автоматическая проверка `scripts/verify.py` копирует данные в отдельный временный
каталог, меняет одно значение, запускает расчёт повторно и проверяет:

1. первый запуск не использует кэш;
2. повторный запуск берёт тот же результат из кэша;
3. изменённые данные создают другой ключ;
4. меняются CSV и SVG;
5. испорченный кэш пересчитывается;
6. ошибочные входные данные останавливают конвейер.

После публикации репозитория окончательная демонстрация P3:

```sh
# Изменить seconds в data/timings.csv на осмысленное новое значение.
git add data/timings.csv
git commit -m "Update experiment observations"
git push origin main
```

Нужно сохранить ссылку на Actions run и сравнить опубликованные `metadata.json`,
CSV и график до/после. Локальная проверка этого поведения уже автоматизирована;
она не выдаётся за состоявшийся push и удалённый деплой.

## Что воспроизводится

Расчёт детерминирован при одинаковом окружении, коде, данных и seed. HTML не обязан
быть побайтно одинаковым: на странице намеренно меняются дата сборки и метаданные
кэша. Bootstrap-интервалы — учебная оценка по малой выборке; для научного вывода
потребуются реальные данные и проверка статистических предпосылок.


---

# Сборка и доставка

## GitHub Pages

Workflow `.github/workflows/site.yml` реализует `check → build → deploy-pages`.
Push в любую ветку и pull request запускают проверку и сборку. Выкладка выполняется
только для `main`, вне pull request. Ручной `workflow_dispatch` может намеренно
добавить битую ссылку: `--strict` остановит job, последующие стадии не запустятся.

В настройках репозитория необходимо выбрать **Settings → Pages → Source: GitHub Actions**.
Полный код workflow находится в архиве исходников. Версии Python и всех пакетов
зафиксированы; actions закреплены за полными SHA официальных репозиториев.
Пакеты кэширует `setup-python`, вычисления — `actions/cache` по ключу входов.

| Подход | Устройство | Права | Компромисс |
| --- | --- | --- | --- |
| push в `gh-pages`, например peaceiris/actions-gh-pages | Скомпилированные файлы коммитятся в отдельную ветку, Pages читает её | `contents: write` либо отдельный ключ/токен | Удобная история файлов, но генерация коммитов и риск перезаписи ветки |
| upload-pages-artifact + deploy-pages | Сборка создаёт artifact, deployment job отправляет его в Pages | `pages: write`, `id-token: write`, environment github-pages | Не нужна ветка с HTML; независимые права сборки и доставки; выбран для проекта |

## Отечественный SSH-хостинг

Для Helios подготовлена отдельная job `deploy-helios`, пока выключенная.
Перед включением нужно создать **отдельный каталог сайта** в `public_html`,
проверить доступ по HTTPS и установить отдельный deploy-ключ с минимальными правами.
Пароль пользователя не используется ни в коде, ни в CI.

| Настройка | Тип | Назначение |
| --- | --- | --- |
| HELIOS_ENABLED | Variable | `true` только после настройки |
| HELIOS_HOST, HELIOS_PORT, HELIOS_USER | Variables | Адрес, порт SSH и логин |
| HELIOS_DIR | Variable | Абсолютный путь выделенного каталога назначения |
| HELIOS_URL | Variable | Публичный HTTPS URL, обязательно с завершающим `/` |
| HELIOS_DEPLOY_KEY | Secret | Приватная часть отдельного deploy-ключа |
| HELIOS_KNOWN_HOSTS | Secret | Проверенный ключ SSH-сервера |
| PAGES_URL | Optional variable | Канонический URL при собственном домене |

Публичный ключ помещается в `authorized_keys` владельцем аккаунта. Для нестандартного
порта запись known_hosts имеет вид `[host]:port`. `ssh-keyscan` лишь получает ключ:
отпечаток нужно сверить с администратором или другим доверенным каналом. Скрипт
использует `StrictHostKeyChecking=yes`; отключать проверку нельзя.

Стандартный клиент SSH использует строчную опцию `-p PORT`.
У `scp` порт задаётся заглавной `-P`. У `rsync` порт передаётся внутрь SSH-команды.

`rsync --delay-updates` задерживает замену файлов до конца передачи, но не делает
переключение всего сайта атомарным. При обрыве возможна смесь старой и новой версии;
повторная доставка исправляет её. Для публикаций с жёсткими требованиями нужны
release-каталоги и атомарная смена симлинка, если политика хостинга это разрешает.
Здесь намеренно нет `--delete`, чтобы не стирать ранее размещённые материалы.

## URL, поиск и автономность

`use_directory_urls: false` сохраняет ссылки вида `generated/results.html`.
Относительные ссылки на CSS, SVG и JS работают и в корне, и в подкаталоге.
`SITE_URL` задаётся отдельно при сборке для Pages и Helios; он нужен для canonical
и sitemap, а не для исправления неверных абсолютных ссылок вручную.

Тема использует системные шрифты (`font: false`), поиск — локальные lunr-скрипты
и индекс с русским языком. Формулы отображаются через MathML. В HTML/CSS не должно
быть внешних исполняемых ресурсов; `scripts/audit_site.py` проверяет это и ссылки.
Браузерная проверка по HTTP необходима: открытие через `file://` мешает поиску.

## Безопасность

Секреты отсутствуют в checkout сборки из форка; deployment не запускается для PR.
Нельзя использовать `pull_request_target` для выполнения недоверенного кода с секретами.
Фиксация actions по SHA защищает от перемещения тега, но не заменяет проверку кода
и обновление зависимостей. Компрометация action с deploy-правами позволяет подменить
публикацию или украсть SSH-ключ. Права надо ограничить конкретным каталогом/окружением.
Скрипт не включает shell trace и удаляет временный ключ по завершении.

После доставки healthcheck требует HTTP 200 и строку `RESEARCH-SITE-3960-OK`.
Это проверяет доступность страницы, но не заменяет проверку поиска и формулы.
Живые результаты внешнего CI, маскирование секретов и время удалённой доставки
будут записаны только после реального запуска, а не по локальной имитации.


---

# Результаты эксперимента

!!! warning "Происхождение данных"
    Синтетический учебный набор, 20 наблюдений. Эти числа не являются замером реальной системы.

## Методика

Для каждой группы рассчитываем среднее время и процентильный 95% bootstrap-интервал
по 20000 выборкам с возвращением, seed=3960. Интервал относится к среднему времени,
а не к ускорению. При пяти наблюдениях в группе неопределённость оценена лишь приближённо.

<div class="formula" id="eq-speedup"><math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><mrow><mi>S</mi><mo>(</mo><mi>p</mi><mo>)</mo><mo>=</mo><mfrac><msub><mover><mi>t</mi><mo>¯</mo></mover><mn>1</mn></msub><msub><mover><mi>t</mi><mo>¯</mo></mover><mi>p</mi></msub></mfrac></mrow></math><span>(1)</span></div>

Ускорение определено в [формуле (1)](#eq-speedup), эффективность равна S(p)/p.
Формула — нативный MathML; загрузка MathJax, шрифтов или CDN не требуется.

## График и таблица

![Среднее время обработки по числу потоков](docs/generated/chart.svg)

| Потоки | n | Среднее, с | 95% CI, с | Ускорение | Эффективность |
| --- | --- | --- | --- | --- | --- |
| 1 | 5 | 12.400 | [12.220; 12.580] | 1.000 | 1.000 |
| 2 | 5 | 6.760 | [6.660; 6.840] | 1.834 | 0.917 |
| 4 | 5 | 4.140 | [4.060; 4.240] | 2.995 | 0.749 |
| 8 | 5 | 3.540 | [3.460; 3.640] | 3.503 | 0.438 |

В учебном наборе ускорение растёт медленнее числа потоков, а эффективность падает.
Это согласуется с наличием последовательной части и накладных расходов, но не устанавливает
их причин и не подтверждает закон Амдала на реальных измерениях.

## Артефакты и версия

- [Таблица CSV](docs/generated/summary.csv)
- [Метаданные JSON](docs/generated/metadata.json)
- Коммит: `uncommitted`; незакоммиченные изменения: `True`.
- Дата сборки UTC: `2026-09-19T09:11:02+00:00`.
- Версия данных SHA-256: `f5f27db508d918eee44c494d1b058615ce1b45c57bddf2621566bb65cac0640b`.
- Ключ кэша: `675cc313e9a9207c6ac8f8db52500523c114a26764f7edcdb94506cad45fbdb2`; попадание: `False`.

[Как повторить эксперимент](docs/generated/../pipeline.md) · [Исследование способов публикации](docs/generated/../research.md)


---

# Лицензии

| Объект | Лицензия | Область действия |
| --- | --- | --- |
| Python, shell, Makefile и конфигурация CI | MIT | Файл LICENSE-CODE в репозитории |
| Авторский текст отчёта и сайта | CC BY 4.0 | Файл LICENSE-CONTENT; при повторном использовании укажите автора |
| Синтетический CSV | CC0 1.0 | Файл LICENSE-DATA |
| MkDocs, Material и другие зависимости | Собственные лицензии пакетов | Лицензии этого проекта их не заменяют |

Автор: Артём Солопов. Ссылки на внешнюю документацию не означают передачу прав
на неё. Формула, таблица и график генерируются из собственных учебных данных.


---

# Приложение: полный workflow

```yaml
name: Research site
on:
  push:
  pull_request:
  workflow_dispatch:
    inputs:
      demonstrate_failure:
        description: 'Intentional strict-build failure for the report'
        type: boolean
        default: false

# Fork PRs can test/build but cannot access deployment credentials.
permissions:
  contents: read
concurrency:
  group: site-${{ github.ref }}
  cancel-in-progress: true

jobs:
  check:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4
        with:
          persist-credentials: false
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5
        with:
          python-version: '3.12.13'
          cache: pip
      - run: python -m pip install -r requirements.txt
      - run: make test
      - run: make build
      - name: Intentional negative example (explicit manual run only)
        if: ${{ inputs.demonstrate_failure }}
        run: |
          printf '\n[broken](does-not-exist.md)\n' >> docs/index.md
          python -m mkdocs build --strict --site-dir .work/negative
      - run: python scripts/audit_site.py .work/site

  build:
    needs: check
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4
        with:
          persist-credentials: false
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5
        with:
          python-version: '3.12.13'
          cache: pip
      - run: python -m pip install -r requirements.txt
      - uses: actions/cache@0057852bfaa89a56745cba8c7296529d2fc39830 # v4
        with:
          path: .work/cache
          key: experiment-${{ runner.os }}-py3.12.13-${{ hashFiles('data/timings.csv', 'scripts/experiment.py', 'requirements.txt') }}
      - name: Resolve Pages base URL
        env:
          REPOSITORY: ${{ github.repository }}
          OWNER: ${{ github.repository_owner }}
          CUSTOM_URL: ${{ vars.PAGES_URL }}
        run: |
          owner="${OWNER,,}"
          repo="${REPOSITORY#*/}"
          url="https://${owner}.github.io/${repo}/"
          if [ "${repo,,}" = "${owner}.github.io" ]; then url="https://${owner}.github.io/"; fi
          echo "SITE_URL=${CUSTOM_URL:-$url}" >> "$GITHUB_ENV"
      - run: make build
      - run: python scripts/audit_site.py .work/site
      - uses: actions/upload-pages-artifact@56afc609e74202658d3ffba0e8f6dda462b719fa # v3
        with:
          path: .work/site
      - name: Build for Helios canonical URL
        if: ${{ vars.HELIOS_URL != '' }}
        env:
          SITE_URL: ${{ vars.HELIOS_URL }}
        run: python -m mkdocs build --strict --site-dir .work/helios
      - uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4
        if: ${{ vars.HELIOS_URL != '' }}
        with:
          name: helios-site
          path: .work/helios
          retention-days: 7

  deploy-pages:
    needs: build
    if: ${{ github.ref == 'refs/heads/main' && github.event_name != 'pull_request' }}
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/configure-pages@983d7736d9b0ae728b81ab479565c72886d7745b # v5
      - id: deployment
        uses: actions/deploy-pages@d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e # v4
      - name: Verify published HTML
        env:
          PAGE_URL: ${{ steps.deployment.outputs.page_url }}
        run: |
          for attempt in 1 2 3 4 5; do
            status=$(curl --silent --show-error --location -o /tmp/health.html -w '%{http_code}' "$PAGE_URL") || status=000
            if [ "$status" = 200 ] && grep -q RESEARCH-SITE-3960-OK /tmp/health.html; then exit 0; fi
            sleep 5
          done
          exit 1

  deploy-helios:
    needs: build
    if: ${{ github.ref == 'refs/heads/main' && github.event_name != 'pull_request' && vars.HELIOS_ENABLED == 'true' }}
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    environment: helios
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4
        with:
          persist-credentials: false
      - uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093 # v4
        with:
          name: helios-site
          path: .work/helios
      - name: Deliver with strict host verification
        env:
          DEPLOY_KEY: ${{ secrets.HELIOS_DEPLOY_KEY }}
          KNOWN_HOSTS: ${{ secrets.HELIOS_KNOWN_HOSTS }}
          SSH_HOST: ${{ vars.HELIOS_HOST }}
          SSH_PORT: ${{ vars.HELIOS_PORT }}
          SSH_USER: ${{ vars.HELIOS_USER }}
          REMOTE_DIR: ${{ vars.HELIOS_DIR }}
          SITE_URL: ${{ vars.HELIOS_URL }}
        run: bash scripts/deploy.sh .work/helios

```

---

## audit.log

```text
audit OK: 8 HTML files, no missing local links or external HTML/CSS assets

```

---

## build.log

```text
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/artem.solopov/Documents/ChatGPT/python-lab/.work/site
INFO    -  Documentation built in 0.22 seconds

```

---

## failure-invalid-data.log

```text
Traceback (most recent call last):
  File "/Users/artem.solopov/Documents/ChatGPT/python-lab/scripts/experiment.py", line 166, in <module>
    main()
  File "/Users/artem.solopov/Documents/ChatGPT/python-lab/scripts/experiment.py", line 93, in main
    groups = read_data(args.data)
             ^^^^^^^^^^^^^^^^^^^^
  File "/Users/artem.solopov/Documents/ChatGPT/python-lab/scripts/experiment.py", line 37, in read_data
    raise ValueError('workers/run must be positive; seconds must be finite and positive')
ValueError: workers/run must be positive; seconds must be finite and positive

```

---

## failure-missing-anchor.log

```text

Aborted with 1 warnings in strict mode!
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/artem.solopov/Documents/ChatGPT/python-lab/.work/verify-hfby69b2/site
WARNING -  Doc file 'index.md' contains a link '#absent', but there is no such anchor on this page.

```

---

## failure-missing-link.log

```text

Aborted with 1 warnings in strict mode!
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/artem.solopov/Documents/ChatGPT/python-lab/.work/verify-hfby69b2/site
WARNING -  Doc file 'index.md' contains a link 'absent.md', but the target is not found among documentation files.

```

---

## negative-fixtures-fixed.log

```text
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/artem.solopov/Documents/ChatGPT/python-lab/.work/verify-hfby69b2/site
INFO    -  Documentation built in 0.04 seconds

```

---

## tests.log

```text
test_known_constant_samples (test_experiment.ExperimentTests.test_known_constant_samples) ... ok
test_reject_nonfinite_and_duplicate (test_experiment.ExperimentTests.test_reject_nonfinite_and_duplicate) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.131s

OK

```