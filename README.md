# CLI приложение для конвертации документов

Терминальное CLI приложение для конвертации .txt файлов в XML формат с сохранением в PostgreSQL БД или в XML файлы.

## Возможности

- Парсинг .txt файлов с русскими параметрами
- Транслитерация русских параметров в английские
- Конвертация в XML формат
- Сохранение в PostgreSQL БД
- Сохранение XML в файлы (работает без БД)
- Таблица для отслеживания уже встреченных параметров
- Поддержка различных стратегий перевода и разделения параметров (задел для LLM)

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите PostgreSQL через Docker:
```bash
docker-compose up -d
```

3. Дождитесь запуска БД (обычно несколько секунд):
```bash
# Проверьте статус контейнера
docker ps
```

4. Сделайте файл main.py исполняемым (на Linux):
```bash
chmod +x main.py
```

## Использование

### Базовое использование:
```bash
python main.py /path/to/documents
```

Или напрямую (если файл исполняемый):
```bash
./main.py /path/to/documents
```

### С флагами:
```bash
# Выбор стратегии перевода
python main.py /path/to/documents --translation-strategy translit

# Выбор стратегии разделения параметров
python main.py /path/to/documents --splitting-strategy llm

# Подробный вывод
python main.py /path/to/documents --verbose

# Указание URL БД
python main.py /path/to/documents --db-url postgresql://user:pass@localhost:5432/dbname

# Сохранение XML в файлы (работает без БД)
python main.py /path/to/documents --output-xml

# Сохранение XML в указанную директорию
python main.py /path/to/documents --output-xml --xml-dir /path/to/output

# Только сохранение в XML файлы без БД
python main.py /path/to/documents --output-xml --no-db

# Сохранение и в БД, и в XML файлы
python main.py /path/to/documents --output-xml --verbose
```

### Все флаги:
- `--translation-strategy`: Стратегия перевода (`translit` или `llm`, по умолчанию: `translit`)
- `--splitting-strategy`: Стратегия разделения длинных параметров (`none` или `llm`, по умолчанию: `none`)
- `--db-url`: URL подключения к БД (по умолчанию: из переменных окружения)
- `-v, --verbose`: Подробный вывод информации
- `--output-xml`: Сохранять XML в файлы (работает без БД)
- `--xml-dir`: Директория для сохранения XML файлов (по умолчанию: рядом с исходными .txt файлами)
- `--no-db`: Не использовать БД (только сохранять в XML файлы)

## Переменные окружения для БД

Настройки БД хранятся в файле `.env` в корне проекта. По умолчанию используются:
- `DB_USER=postgres`
- `DB_PASSWORD=postgres`
- `DB_HOST=localhost`
- `DB_PORT=5432`
- `DB_NAME=documents_db`

Вы можете изменить эти значения в файле `.env` или установить переменные окружения в системе.

## Формат входных .txt файлов

```
Название документа
- Параметр1;
- Параметр2;
- Параметр3;
```

## Формат выходных XML файлов

```xml
<document>
    <param1></param1>
    <param2></param2>
    <param3></param3>
</document>
```

## Структура БД

### Таблица `documents`
- `id`: Идентификатор
- `original_filename`: Имя исходного .txt файла
- `document_name`: Название документа
- `xml_content`: XML содержимое документа
- `created_at`: Дата создания

### Таблица `parameters`
- `id`: Идентификатор
- `russian_name`: Русское название параметра (уникальное)
- `english_name`: Английское название параметра
- `created_at`: Дата создания

## Пример использования

1. Создайте директорию с .txt файлами:
```bash
mkdir test_documents
cp test_example.txt test_documents/
```

2. Запустите обработку:
```bash
python main.py test_documents --verbose
```

3. Проверьте результат в БД:
```bash
docker exec -it documents_postgres psql -U postgres -d documents_db -c "SELECT * FROM documents;"
docker exec -it documents_postgres psql -U postgres -d documents_db -c "SELECT * FROM parameters;"
```

## Задел для будущего развития

В коде оставлены заделы для интеграции LLM:
- Функция `translate_with_strategy()` в `transliteration.py` - готовность к добавлению LLM перевода
- Функция `split_parameter_with_strategy()` в `transliteration.py` - готовность к добавлению LLM разделения параметров

Места для расширения помечены комментариями `# TODO: Реализовать использование LLM...`

