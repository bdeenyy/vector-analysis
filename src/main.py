# src/main.py
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
        # Очистка временных файлов matplotlib
        matplotlib_cache = os.path.join(tempfile.gettempdir(), 'matplotlib')
        if os.path.exists(matplotlib_cache):
            shutil.rmtree(matplotlib_cache, ignore_errors=True)

        # Очистка временной директории PyInstaller
        temp_dir = getattr(sys, '_MEIPASS', None)
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

        # Очистка других временных файлов приложения
        app_temp = os.path.join(tempfile.gettempdir(), 'VectorAnalyzer_temp')
        if os.path.exists(app_temp):
            shutil.rmtree(app_temp, ignore_errors=True)
    except Exception:
        # Игнорируем ошибки при очистке
        pass


if __name__ == '__main__':
    # Регистрация функции очистки
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

    # Очистка перед выходом
    cleanup_temp()

    sys.exit(exit_code)