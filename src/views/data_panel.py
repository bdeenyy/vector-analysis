# src/views/data_panel.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from src.components.custom_table import CustomTable
from src.components.styled_widgets import StyledFrame, StyledTitle, StyledButton


class DataPanel(QWidget):
    """
    Панель с таблицей данных и элементами управления
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Создаем таблицу до setup_ui
        self.table = CustomTable()
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        layout.addWidget(self._create_header())

        # Table container
        layout.addWidget(self._create_table_container())

    def _create_header(self):
        """Создание заголовка"""
        header = StyledFrame()
        header_layout = QVBoxLayout(header)

        title = StyledTitle("Анализ векторных данных")
        subtitle = QLabel("Введите или импортируйте данные для анализа")
        subtitle.setStyleSheet("color: #666666;")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        return header

    def _create_table_container(self):
        """Создание контейнера с таблицей"""
        container = StyledFrame()
        layout = QVBoxLayout(container)

        # Table header with controls
        header = self._create_table_header()
        layout.addWidget(header)

        # Add table to container
        layout.addWidget(self.table)

        return container

    def _create_table_header(self):
        """Создание заголовка таблицы с кнопками управления"""
        header = QWidget()
        layout = QHBoxLayout(header)

        title = StyledTitle("Данные измерений")
        layout.addWidget(title)

        # Control buttons
        buttons = QWidget()
        buttons_layout = QHBoxLayout(buttons)
        buttons_layout.setSpacing(4)

        remove_btn = StyledButton("-", style_type="circular")
        remove_btn.clicked.connect(self.table.delete_row)

        add_btn = StyledButton("+", style_type="circular")
        add_btn.clicked.connect(self.table.add_row)

        buttons_layout.addWidget(remove_btn)
        buttons_layout.addWidget(add_btn)
        layout.addWidget(buttons)

        return header

    def get_table(self):
        """Получить ссылку на таблицу"""
        return self.table