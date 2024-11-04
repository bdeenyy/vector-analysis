# Анализатор Вертикальных Отклонений

Приложение для расчета и визуализации векторных диаграмм и вертикальных отклонений конструкций. 

## Возможности

- Расчет и визуализация векторных диаграмм
- Анализ вертикальных отклонений с учетом допусков
- Импорт данных из Excel
- Экспорт результатов в PDF
- Интерактивный пользовательский интерфейс

## Требования

- Python 3.8 или выше
- PyQt6
- Matplotlib
- NumPy
- pandas
- Установленные шрифты с поддержкой кириллицы

## Установка

1. Клонировать репозиторий:
```bash
git clone https://github.com/your-username/vector-analysis.git
cd vector-analysis
```

2. Создать виртуальное окружение:
```bash
python -m venv venv
```

3. Активировать виртуальное окружение:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/macOS:
```bash
source venv/bin/activate
```

4. Установить зависимости:
```bash
pip install -r requirements.txt
```

## Использование

1. Запустить приложение:
```bash
python main.py
```

2. Ввод данных:
   - Ввести данные вручную в таблицу
   - Импортировать данные из Excel
   - Вставить данные из буфера обмена

3. Настройка параметров:
   - Задать азимут
   - Выбрать направление (по часовой/против часовой)
   - Установить допустимое отклонение

4. Анализ результатов:
   - Просмотр векторных диаграмм
   - Анализ графиков отклонений
   - Экспорт результатов в PDF


## Формат входных данных

Excel файл должен содержать следующие колонки:
1. Сечение (м)
2. ОП1 (мм)
3. ОП2 (мм)
4. ОП3 (мм)

## Разработка

### Установка среды разработки

1. Установить дополнительные инструменты для разработки:
```bash
pip install -r requirements-dev.txt
```

2. Настроить pre-commit хуки:
```bash
pre-commit install
```

### Тестирование

Запуск тестов:
```bash
pytest
```

## Лицензия

[MIT License](LICENSE)

## Авторы

- Ваше имя или организация

## Поддержка

При возникновении проблем, пожалуйста, создайте issue в репозитории проекта.