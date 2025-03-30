# TF-IDF Анализатор текста

Веб-приложение для анализа текстовых файлов с использованием алгоритма TF-IDF (Term Frequency - Inverse Document Frequency).

## Описание проекта

TF-IDF Анализатор - это веб-приложение, которое позволяет выполнять анализ текстовых файлов на русском языке, рассчитывая значения TF (частота термина) и IDF (обратная частота документа) для слов в тексте. Это полезно для определения значимости слов в документе относительно коллекции документов.

Основные возможности:
- Загрузка текстовых файлов через веб-интерфейс
- Автоматическая токенизация и фильтрация русского текста (удаление стоп-слов, пунктуации, цифр)
- Расчет показателей TF для каждого слова в документе
- Расчет показателей IDF относительно всех ранее загруженных документов
- Отображение 50 наиболее значимых слов, отсортированных по убыванию значения IDF

## Технический стек

- **Backend**: FastAPI, Python 3
- **База данных**: SQLite с SQLModel (ORM)
- **Обработка текста**: NLTK, razdel
- **Frontend**: HTML, Bootstrap 5
- **Шаблонизатор**: Jinja2
- **Веб-сервер**: Uvicorn

## Установка и запуск

### Предварительные требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)

### Шаги установки

1. Клонируйте репозиторий:
```bash
git clone https://github.com/amoglock/intership_lesta.git
cd itership_lesta
```

2. Создайте и активируйте виртуальное окружение (опционально, но рекомендуется):
```bash
python -m venv venv
source venv/bin/activate  # Для Linux/macOS
# или
venv\Scripts\activate     # Для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Запустите сервер:
```bash
uvicorn src.main:app --reload
```

5. Откройте веб-браузер и перейдите по адресу:
```
http://localhost:8000
```

## Использование

1. Откройте приложение в веб-браузере.
2. Нажмите кнопку "Выбрать файл" и выберите текстовый файл для анализа (.txt).
3. Нажмите кнопку "Анализировать".
4. После обработки вы увидите таблицу с результатами анализа, содержащую:
   - Слова из документа
   - Значения TF (частота слова в документе)
   - Значения IDF (обратная частота документа)

Результаты отсортированы по убыванию значения IDF, что позволяет видеть наиболее редкие и потенциально наиболее значимые слова вверху таблицы.

## Как это работает

### TF (Term Frequency)

Частота термина показывает, насколько часто слово встречается в документе. Рассчитывается по формуле:

```
TF(слово) = (Количество вхождений слова в документе) / (Общее количество слов в документе)
```

### IDF (Inverse Document Frequency)

Обратная частота документа показывает, насколько редко слово встречается во всей коллекции документов. Рассчитывается по формуле:

```
IDF(слово) = log((Общее количество документов + 1) / (Количество документов, содержащих слово + 1))
```

Добавление единицы к числителю и знаменателю (сглаживание) помогает избежать деления на ноль и обеспечивает более стабильные результаты.

### Обработка текста

1. Текст токенизируется с помощью библиотеки razdel, специально разработанной для русского языка.
2. Удаляются стоп-слова (частые служебные слова, не несущие смысловой нагрузки).
3. Удаляются знаки пунктуации, цифры и пробельные символы.
4. Для каждого слова рассчитываются значения TF и IDF.
5. Результаты сортируются по убыванию значения IDF и выводятся 50 верхних слов.

## Структура проекта

```
src/
├── core/               # Основные настройки и утилиты
│   └── config.py       # Конфигурация приложения
├── tf_idf/             # Модуль обработки TF-IDF
│   ├── processor.py    # Процессор для анализа текста
│   ├── repository.py   # Работа с базой данных
│   ├── router.py       # Маршруты FastAPI
│   └── models.py       # Модели данных для TF-IDF
├── static/             # Статические файлы (CSS, JS)
├── templates/          # Шаблоны HTML
│   └── upload.html     # Шаблон для загрузки и отображения результатов
├── models.py           # Модели данных SQLModel
├── database.py         # Настройка базы данных
└── main.py             # Основной файл приложения
```
