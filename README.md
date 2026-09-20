# Задание 1 — публикация воспроизводимых исследований

**Артём Солопов.** Основной ход работы, T2 и P3.

Готовая локальная работа: [единый отчёт](REPORT.md), исходники сайта в `docs/`,
конвейер в `scripts/`, зафиксированное окружение в `requirements.txt`.
Итоговый HTML и ZIP для передачи находятся в `artifacts/`.
Репозиторий: https://github.com/de6igz/python-lab

GitHub Pages: https://de6igz.github.io/python-lab/

Helios ИТМО: https://se.ifmo.ru/~s332961/python-lab/

Обе площадки публикуются автоматически через Actions. На Helios используется
отдельный ограниченный deploy-ключ и проверка HTTP после доставки.
Паролей или приватных ключей в проекте нет.

## Повторить сборку

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
make test
make build
make serve
```

`make build` создаёт `.work/site/`; `make serve` открывает сервер на localhost:8000.
Проверки кэша, изменения данных и отрицательные тесты:

```sh
python scripts/verify.py
```

Этот запуск перезаписывает измерения в `evidence/`; длительность зависит от машины.
Исходный CSV не меняется, тестовая мутация выполняется в изолированной копии.

## Посмотреть готовую сборку без установки MkDocs

```sh
python3 scripts/preview.py --directory artifacts --port 8001
```

Открыть `http://127.0.0.1:8001/site/`. Сервер блокирует внешние ресурсы через CSP,
что позволяет проверить автономность формулы, шрифтов и поиска. Остановить — Ctrl+C.

## Проверенная публикация

- [Успешный CI](https://github.com/de6igz/python-lab/actions/runs/35435796768).
- [Намеренный сбой strict build](https://github.com/de6igz/python-lab/actions/runs/35436124108): отсутствующая страница блокирует доставку.
- [Обновление CSV и сайта](https://github.com/de6igz/python-lab/actions/runs/35436253645): среднее для 8 потоков изменилось с 3.540 до 3.340 с.
- Обе площадки возвращают HTTP 200 и контрольную строку; на обеих проверен русский поиск.

[Автопубликация обеих площадок](https://github.com/de6igz/python-lab/actions/runs/35536497862)
проверена: Helios — 14 с, Pages — 8 с. Три скриншота сайта опубликованы.
Остаётся приложить скриншот проваленного CI и сдать работу в Moodle.

## Лицензии

Код — MIT, текст — CC BY 4.0, синтетические данные — CC0-1.0.
