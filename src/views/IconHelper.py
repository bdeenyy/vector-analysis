import os
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

# Размер иконок по умолчанию
ICON_SIZE = QSize(16, 16)

# Карта соответствия имен иконок и файлов
ICON_MAP = {
    'excel': 'table.png',
    'clipboard': 'clipboard.png',
    'calculate': 'calculator.png',
    'clockwise': 'rotate-cw.png',
    'counterclockwise': 'rotate-ccw.png',
    'pdf': 'file-text.png',
    'plus': 'plus-circle.png',
    'minus': 'minus-circle.png',
    'refresh': 'refresh.png'
}


def get_icon_path(name):
    """
    Получить полный путь к файлу иконки
    """
    if name not in ICON_MAP:
        return None

    # Получаем путь к текущему файлу
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Поднимаемся на уровень выше к src
    src_dir = os.path.dirname(current_dir)

    # Формируем путь к иконке
    icon_path = os.path.join(src_dir, 'resources', 'icons', ICON_MAP[name])

    # Проверяем существование файла
    if os.path.exists(icon_path):
        print(f"Icon found: {icon_path}")  # Для отладки
        return icon_path
    else:
        print(f"Icon not found: {icon_path}")  # Для отладки
        return None


def get_icon(name):
    """
    Получить иконку по имени
    """
    icon_path = get_icon_path(name)
    if icon_path:
        return QIcon(icon_path)
    return QIcon()


def setup_button_with_icon(button, icon_name):
    """
    Установить иконку для кнопки
    """
    icon = get_icon(icon_name)
    if not icon.isNull():
        button.setIcon(icon)
        button.setIconSize(ICON_SIZE)