# src/views/control_panel.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QRadioButton,
    QLabel, QSlider, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal
from src.components.styled_widgets import StyledFrame, StyledTitle, StyledButton
from src.views import IconHelper


class ImportGroup(StyledFrame):
    """Группа компонентов для импорта данных"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Заголовок
        title = StyledTitle("Импорт данных")
        layout.addWidget(title)

        # Кнопки импорта
        self.excel_btn = StyledButton("Загрузить Excel")
        IconHelper.setup_button_with_icon(self.excel_btn, "excel")
        layout.addWidget(self.excel_btn)

        self.clipboard_btn = StyledButton("Вставить из буфера")
        IconHelper.setup_button_with_icon(self.clipboard_btn, "clipboard")
        layout.addWidget(self.clipboard_btn)


class DirectionSlider(QWidget):
    """Слайдер для выбора азимута"""

    value_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Заголовок и значение
        header = QHBoxLayout()
        self.label = QLabel("Азимут")
        self.value_label = QLabel("0°")
        header.addWidget(self.label)
        header.addWidget(self.value_label)
        layout.addLayout(header)

        # Слайдер
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 360)
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)

    def _on_value_changed(self, value):
        self.value_label.setText(f"{value}°")
        self.value_changed.emit(value)

    def value(self):
        return self.slider.value()


class DirectionGroup(StyledFrame):
    """Группа компонентов для управления направлением"""

    direction_changed = pyqtSignal(bool)  # True для по часовой, False против
    azimuth_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Заголовок
        title = StyledTitle("Направление")
        layout.addWidget(title)

        # Слайдер азимута
        self.azimuth_slider = DirectionSlider()
        self.azimuth_slider.value_changed.connect(self.azimuth_changed)
        layout.addWidget(self.azimuth_slider)

        # Радио кнопки направления
        self.direction_group = QButtonGroup(self)

        self.clockwise = QRadioButton("По часовой")
        IconHelper.setup_button_with_icon(self.clockwise, "clockwise")
        self.clockwise.setStyleSheet(self._get_radio_style())

        self.counterclockwise = QRadioButton("Против часовой")
        IconHelper.setup_button_with_icon(self.counterclockwise, "counterclockwise")
        self.counterclockwise.setStyleSheet(self._get_radio_style())

        self.clockwise.setChecked(True)

        self.direction_group.addButton(self.clockwise)
        self.direction_group.addButton(self.counterclockwise)

        layout.addWidget(self.clockwise)
        layout.addWidget(self.counterclockwise)

        # Подключение сигналов
        self.clockwise.toggled.connect(self._on_direction_changed)

    def _get_radio_style(self):
        return """
            QRadioButton {
                padding: 8px;
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                margin-top: 4px;
            }
            QRadioButton:hover {
                background-color: #f9fafb;
            }
            QRadioButton:checked {
                border-color: #2563eb;
                color: #2563eb;
            }
        """

    def _on_direction_changed(self, checked):
        self.direction_changed.emit(checked)

    def get_values(self):
        """Получить текущие значения настроек"""
        return {
            'azimuth': self.azimuth_slider.value(),
            'is_clockwise': self.clockwise.isChecked()
        }


class ControlPanel(QWidget):
    """Основная панель управления"""

    calculate_clicked = pyqtSignal()
    direction_changed = pyqtSignal(bool)
    azimuth_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        self.setFixedWidth(320)
        self.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
                border-left: 1px solid #e5e7eb;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Группа импорта
        self.import_group = ImportGroup()
        layout.addWidget(self.import_group)

        # Группа направления
        self.direction_group = DirectionGroup()
        layout.addWidget(self.direction_group)

        # Растягивающийся промежуток
        layout.addStretch()

        # Кнопка расчета
        self.calculate_btn = StyledButton("Рассчитать", style_type="primary")
        IconHelper.setup_button_with_icon(self.calculate_btn, "calculate")
        layout.addWidget(self.calculate_btn)

    def connect_signals(self):
        self.calculate_btn.clicked.connect(self.calculate_clicked)
        self.direction_group.direction_changed.connect(self.direction_changed)
        self.direction_group.azimuth_changed.connect(self.azimuth_changed)

    def get_direction_values(self):
        return self.direction_group.get_values()

    @property
    def excel_button(self):
        return self.import_group.excel_btn

    @property
    def clipboard_button(self):
        return self.import_group.clipboard_btn