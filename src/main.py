import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.views.main_window import MainWindow


def check_resources():
    """Проверка наличия ресурсов"""
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Проверка иконок
    icons_dir = os.path.join(current_dir, 'resources', 'icons')
    if os.path.exists(icons_dir):
        print(f"Icons directory found: {icons_dir}")
        for icon_file in os.listdir(icons_dir):
            print(f"Found icon: {icon_file}")
    else:
        print(f"Icons directory not found: {icons_dir}")

    # Проверка шрифтов
    fonts_dir = os.path.join(current_dir, 'resources', 'fonts')
    if os.path.exists(fonts_dir):
        print(f"Fonts directory found: {fonts_dir}")
        for font_file in os.listdir(fonts_dir):
            print(f"Found font: {font_file}")
    else:
        print(f"Fonts directory not found: {fonts_dir}")


if __name__ == '__main__':
    check_resources()  # Добавьте эту строку перед созданием QApplication
    app = QApplication(sys.argv)

    # Set application icon
    icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())