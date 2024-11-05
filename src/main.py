import sys
import os
import shutil
import atexit
import tempfile
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.views.main_window import MainWindow


def cleanup_temp():
    """Очистка временных файлов при выходе"""
    try:
        # Получаем путь к временной директории PyInstaller
        temp_dir = getattr(sys, '_MEIPASS', None)
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        # Игнорируем ошибки при очистке
        pass


if __name__ == '__main__':
    # Регистрируем функцию очистки
    atexit.register(cleanup_temp)

    app = QApplication(sys.argv)

    # Установка иконки приложения
    icon_path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'icon.ico'
    )
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Создание и отображение главного окна
    window = MainWindow()
    window.show()

    # Запуск приложения
    exit_code = app.exec()

    # Явная очистка перед выходом
    cleanup_temp()

    sys.exit(exit_code)