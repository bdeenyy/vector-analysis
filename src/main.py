import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.views.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Set application icon
    icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())