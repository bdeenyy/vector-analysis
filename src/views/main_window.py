from typing import List, Optional, Tuple
from dataclasses import dataclass
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QRadioButton, QLabel, QLineEdit,
    QTabWidget, QButtonGroup, QMessageBox, QApplication, QGridLayout,
    QScrollArea
)
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import pyqtSlot
from src.models.vector_data import VectorData
from src.views.VerticalDeviationPlot import VerticalDeviationPlot
from src.views.vector_plot import VectorPlot
from src.utils.excel_handler import ExcelHandler


@dataclass
class UIConfig:
    """Configuration constants for UI"""
    WINDOW_TITLE = "Vector Analysis"
    WINDOW_GEOMETRY = (100, 100, 1200, 800)
    DEFAULT_ROWS = 2
    DEFAULT_COLUMNS = 4
    COLUMN_HEADERS = ["Сечение", "ОП1", "ОП2", "ОП3"]
    DEFAULT_TOLERANCE = "1.0"
    DEFAULT_AZIMUTH = "0"


class TableManager:
    """Handles table operations"""

    def __init__(self, table: QTableWidget):
        self.table = table
        self._setup_table()

    def _setup_table(self) -> None:
        """Initialize table properties"""
        self.table.setRowCount(UIConfig.DEFAULT_ROWS)
        self.table.setColumnCount(UIConfig.DEFAULT_COLUMNS)
        self.table.setHorizontalHeaderLabels(UIConfig.COLUMN_HEADERS)
        self.table.horizontalHeader().setStretchLastSection(True)

    def add_row(self) -> None:
        """Add new row to table"""
        self.table.insertRow(self.table.rowCount())

    def delete_row(self) -> None:
        """Delete selected row from table"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def paste_from_clipboard(self) -> None:
        """Paste data from clipboard"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()

        rows = text.strip().split('\n')
        for row_idx, row in enumerate(rows):
            if row_idx >= self.table.rowCount():
                self.table.insertRow(self.table.rowCount())

            columns = row.strip().split('\t')
            for col_idx, value in enumerate(columns[:UIConfig.DEFAULT_COLUMNS]):
                item = QTableWidgetItem(value)
                self.table.setItem(row_idx, col_idx, item)

    def get_data(self) -> List[VectorData]:
        """Get data from table"""
        data = []
        for row in range(self.table.rowCount()):
            try:
                vector_data = self._parse_row(row)
                if vector_data:
                    data.append(vector_data)
            except ValueError:
                continue
        return data

    def _parse_row(self, row: int) -> Optional[VectorData]:
        """Parse single table row"""
        try:
            name = self._get_cell_text(row, 0)
            length1 = float(self._get_cell_text(row, 1) or 0)
            length2 = float(self._get_cell_text(row, 2) or 0)
            length3 = float(self._get_cell_text(row, 3) or 0)

            if any([length1, length2, length3]):  # Skip empty rows
                return VectorData(name, length1, length2, length3)
        except ValueError:
            pass
        return None

    def _get_cell_text(self, row: int, col: int) -> str:
        """Get cell text with safety check"""
        item = self.table.item(row, col)
        return item.text() if item else ""

    def update_from_vector_data(self, data_list: List[VectorData]) -> None:
        """Update table from vector data list"""
        self.table.setRowCount(0)
        for vector_data in data_list:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(vector_data.name)))
            self.table.setItem(row, 1, QTableWidgetItem(str(vector_data.length1)))
            self.table.setItem(row, 2, QTableWidgetItem(str(vector_data.length2)))
            self.table.setItem(row, 3, QTableWidgetItem(str(vector_data.length3)))


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.table_manager = None
        self.excel_handler = ExcelHandler()
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize user interface"""
        self.setWindowTitle(UIConfig.WINDOW_TITLE)
        self.setGeometry(*UIConfig.WINDOW_GEOMETRY)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.tabs = QTabWidget()
        self.setup_tabs()

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.tabs)

    def setup_tabs(self) -> None:
        """Setup all tabs"""
        self.data_tab = QWidget()
        self.vector_tab = QWidget()
        self.deviation_tab = QWidget()

        self.setup_data_tab()
        self.setup_vector_tab()
        self.setup_deviation_tab()

        self.tabs.addTab(self.data_tab, "Данные")
        self.tabs.addTab(self.vector_tab, "Векторы")
        self.tabs.addTab(self.deviation_tab, "Отклонения")

    def setup_data_tab(self) -> None:
        """Setup data input tab"""
        layout = QHBoxLayout()

        # Table setup
        self.table = QTableWidget()
        self.table_manager = TableManager(self.table)
        layout.addWidget(self.table)

        # Controls panel
        controls = self._create_control_panel()
        layout.addLayout(controls)

        self.data_tab.setLayout(layout)

    def _create_control_panel(self) -> QVBoxLayout:
        """Create control panel layout"""
        controls = QVBoxLayout()

        # Azimuth input
        azimuth_layout = self._create_azimuth_input()
        controls.addLayout(azimuth_layout)

        # Direction radio buttons
        direction_layout = self._create_direction_controls()
        controls.addLayout(direction_layout)

        # Action buttons
        self._create_action_buttons(controls)

        controls.addStretch()
        return controls

    def _create_azimuth_input(self) -> QHBoxLayout:
        """Create azimuth input layout"""
        layout = QHBoxLayout()
        self.azimuth_label = QLabel("Азимут:")
        self.azimuth_input = QLineEdit(UIConfig.DEFAULT_AZIMUTH)
        self.azimuth_input.setValidator(QDoubleValidator())
        layout.addWidget(self.azimuth_label)
        layout.addWidget(self.azimuth_input)
        return layout

    def _create_direction_controls(self) -> QVBoxLayout:
        """Create direction control layout"""
        layout = QVBoxLayout()
        self.direction_group = QButtonGroup()
        self.clockwise = QRadioButton("По часовой")
        self.counterclockwise = QRadioButton("Против часовой")
        self.clockwise.setChecked(True)
        self.direction_group.addButton(self.clockwise)
        self.direction_group.addButton(self.counterclockwise)
        layout.addWidget(self.clockwise)
        layout.addWidget(self.counterclockwise)
        return layout

    def _create_action_buttons(self, layout: QVBoxLayout) -> None:
        """Create and add action buttons"""
        buttons = [
            ("calculate_btn", "Рассчитать", self.calculate),
            ("paste_btn", "Вставить из буфера", self.table_manager.paste_from_clipboard),
            ("add_row_btn", "Добавить строку", self.table_manager.add_row),
            ("delete_row_btn", "Удалить строку", self.table_manager.delete_row),
            ("load_excel_btn", "Загрузить Excel", self.load_excel)
        ]

        for attr_name, text, slot in buttons:
            button = QPushButton(text)
            button.clicked.connect(slot)
            setattr(self, attr_name, button)
            layout.addWidget(button)

    def setup_vector_tab(self) -> None:
        """Setup vector visualization tab"""
        layout = QVBoxLayout()
        self.vector_container = QWidget()
        self.vector_container.setLayout(QGridLayout())

        scroll = QScrollArea()
        scroll.setWidget(self.vector_container)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.vector_tab.setLayout(layout)

    def setup_deviation_tab(self) -> None:
        """Setup deviation visualization tab"""
        layout = QVBoxLayout()

        controls = self._create_deviation_controls()
        layout.addLayout(controls)

        self.deviation_container = QWidget()
        self.deviation_container.setLayout(QHBoxLayout())

        scroll = QScrollArea()
        scroll.setWidget(self.deviation_container)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.deviation_tab.setLayout(layout)

    def _create_deviation_controls(self) -> QHBoxLayout:
        """Create deviation control layout"""
        controls = QHBoxLayout()

        tolerance_layout = QHBoxLayout()
        self.tolerance_label = QLabel("Допустимое отклонение (мм/м):")
        self.tolerance_input = QLineEdit(UIConfig.DEFAULT_TOLERANCE)
        self.tolerance_input.setValidator(QDoubleValidator(0.0, 100.0, 2))
        tolerance_layout.addWidget(self.tolerance_label)
        tolerance_layout.addWidget(self.tolerance_input)

        self.update_deviation_btn = QPushButton("Обновить графики")
        self.update_deviation_btn.clicked.connect(self.update_deviation_plots)

        controls.addLayout(tolerance_layout)
        controls.addWidget(self.update_deviation_btn)
        controls.addStretch()

        return controls

    @pyqtSlot()
    def calculate(self) -> None:
        """Calculate and display results"""
        try:
            data = self.table_manager.get_data()
            if not data:
                raise ValueError("Нет данных для расчета")

            azimuth = float(self.azimuth_input.text())
            is_clockwise = self.clockwise.isChecked()

            self.update_vector_plots(data, azimuth, is_clockwise)
            self.update_deviation_plots()
            self.tabs.setCurrentIndex(1)

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Критическая ошибка", f"Неожиданная ошибка: {str(e)}")

    def update_vector_plots(self, data: List[VectorData], azimuth: float,
                            is_clockwise: bool) -> None:
        """Update vector diagram plots"""
        self._clear_container(self.vector_container)

        for i, vector_data in enumerate(data):
            plot = VectorPlot(self)
            plot.plot_vector_diagram(vector_data, azimuth, is_clockwise)
            self.vector_container.layout().addWidget(plot, i // 3, i % 3)

    def update_deviation_plots(self) -> None:
        """Update deviation plots"""
        try:
            data = self.table_manager.get_data()
            if not data:
                return

            tolerance = float(self.tolerance_input.text())
            self._clear_container(self.deviation_container)

            for i in range(3):
                plot = VerticalDeviationPlot(self)
                plot.plot_deviations(data, i, tolerance)
                self.deviation_container.layout().addWidget(plot)

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    @staticmethod
    def _clear_container(container: QWidget) -> None:
        """Clear all widgets from container"""
        while container.layout().count():
            item = container.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def load_excel(self):
        """Load data from Excel file"""
        try:
            excel_handler = ExcelHandler()
            data_list = excel_handler.load_from_excel()

            if data_list:
                # Clear existing table
                self.table.setRowCount(0)

                # Fill table with new data
                for vector_data in data_list:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(str(vector_data.name)))
                    self.table.setItem(row, 1, QTableWidgetItem(str(vector_data.length1)))
                    self.table.setItem(row, 2, QTableWidgetItem(str(vector_data.length2)))
                    self.table.setItem(row, 3, QTableWidgetItem(str(vector_data.length3)))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке данных: {str(e)}")