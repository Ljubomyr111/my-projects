# 🧠 Telegram-бот для досліджень

Бот, який шукає інформацію в інтернеті, збирає її та створює й надсилає файли (Markdown, Word, Excel, PDF) прямо в Telegram.

## Запуск

Двічі клацни `start.bat` (або `node bot.mjs`). Батник сам перезапускає бота після збою.

## Що вміє

| Інструмент | Що робить |
|---|---|
| `web_search` | пошук в інтернеті (DuckDuckGo) |
| `web_fetch` | читання сторінки за URL |
| `save_file` | зберегти текстовий файл (.md/.txt/.csv/.json/.html) |
| `make_docx` | створити Word (.docx) з Markdown |
| `make_xlsx` | створити Excel (.xlsx) з CSV/JSON |
| `make_pdf` | створити PDF з Markdown (через headless Edge) |
| `send_file` | надіслати файл у Telegram |
| `list_files` | список створених файлів |

## Приклади запитів

```
Знайди інформацію про фотосинтез і зроби звіт у Word
Зроби Excel-таблицю: порівняння iPhone 15 і Samsung S24 за ціною, камерою, батареєю
Підготуй PDF-конспект на тему "історія України, 1917–1921"
Знайди останні новини про штучний інтелект
```

Бот сам: шукає → читає джерела → формує текст → створює файл → надсилає його.

## Команди

- `/help` — меню
- `/files` — список створених файлів
- `/id` — твій Telegram ID

## Структура

- `bot.mjs` — головний файл (Node, без зовнішніх залежностей)
- `config.json` — токен, API-ключ, налаштування
- `helpers/make_docx.py` — Markdown → Word (python-docx)
- `helpers/make_xlsx.py` — CSV/JSON → Excel (openpyxl)
- `files/` — створені файли

## Залежності

- Node.js (вбудований `fetch`, без npm-пакетів)
- Python з `python-docx` і `openpyxl` (вже в комплекті)
- Microsoft Edge (для PDF)

## Безпека

- Тільки власник (`adminChatIds` у config.json) може користуватися ботом.
- Токен і API-ключ лежать у `config.json` — не публікуй цю папку.
