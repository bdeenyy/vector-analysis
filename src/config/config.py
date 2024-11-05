# src/config/config.py

class AppConfig:
    """Конфигурация приложения"""

    # Общие настройки
    APP_NAME = "VectorAnalyzer"
    VERSION = "1.0.0"

    # Настройки очистки файлов
    TEMP_FILES_TTL_DAYS = 1
    LOG_FILES_TTL_DAYS = 30

    # Настройки графиков
    PLOT_DPI = 100
    PLOT_FORMAT = 'png'

    # Настройки интерфейса
    FONT_SIZE = 14
    RESULT_FONT_SIZE = 18

    # Настройки экспорта
    PDF_DPI = 300
    EXCEL_ENCODING = 'utf-8'

    # Пути к ресурсам (относительно корня приложения)
    RESOURCES_DIR = 'resources'
    ICONS_DIR = 'resources/icons'
    FONTS_DIR = 'resources/fonts'