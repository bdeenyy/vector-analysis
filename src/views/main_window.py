
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QRadioButton, QLabel,
    QLineEdit, QTabWidget, QButtonGroup, QFileDialog, QMessageBox, QApplication)
from PyQt6.QtGui import QDoubleValidator
from src.models.vector_data import VectorData
from src.views.VerticalDeviationPlot import VerticalDeviationPlot
from src.views.vector_plot import VectorPlot
from src.utils.excel_handler import ExcelHandler
from PyQt6.QtWidgets import QGridLayout, QScrollArea

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Vector Analysis")
        self.setGeometry(100, 100, 1200, 800)

        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create tab widget
        self.tabs = QTabWidget()
        self.data_tab = QWidget()
        self.vector_tab = QWidget()
        self.deviation_tab = QWidget()

        self.setup_data_tab()
        self.setup_vector_tab()
        self.setup_deviation_tab()

        self.tabs.addTab(self.data_tab, "Данные")
        self.tabs.addTab(self.vector_tab, "Векторы")
        self.tabs.addTab(self.deviation_tab, "Отклонения")

        # Main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.tabs)

    def setup_deviation_tab(self):
        """Setup the deviation visualization tab"""
        layout = QVBoxLayout()

        # Add controls for tolerance settings
        controls_layout = QHBoxLayout()

        # Tolerance input
        tolerance_layout = QHBoxLayout()
        self.tolerance_label = QLabel("Допустимое отклонение (мм/м):")
        self.tolerance_input = QLineEdit("1.0")  # Default value
        self.tolerance_input.setValidator(QDoubleValidator(0.0, 100.0, 2))
        tolerance_layout.addWidget(self.tolerance_label)
        tolerance_layout.addWidget(self.tolerance_input)

        # Update button
        self.update_deviation_btn = QPushButton("Обновить графики")
        self.update_deviation_btn.clicked.connect(self.update_deviation_plots)

        controls_layout.addLayout(tolerance_layout)
        controls_layout.addWidget(self.update_deviation_btn)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Create container for plots
        self.deviation_container = QWidget()
        self.deviation_container.setLayout(QHBoxLayout())

        # Add to scroll area
        scroll = QScrollArea()
        scroll.setWidget(self.deviation_container)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.deviation_tab.setLayout(layout)

    def setup_vector_tab(self):
        """Setup the vector visualization tab"""
        layout = QVBoxLayout()

        # Create container for vector plots
        self.vector_container = QWidget()
        self.vector_container.setLayout(QGridLayout())

        # Add to scroll area
        scroll = QScrollArea()
        scroll.setWidget(self.vector_container)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.vector_tab.setLayout(layout)

    def setup_data_tab(self):
        """Setup the data input tab"""
        layout = QHBoxLayout()

        # Table setup
        self.table = QTableWidget(2, 4)
        self.table.setHorizontalHeaderLabels(["Сечение", "ОП1", "ОП2", "ОП3"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Controls panel
        controls_layout = QVBoxLayout()

        # Azimuth input
        azimuth_layout = QHBoxLayout()
        self.azimuth_label = QLabel("Азимут:")
        self.azimuth_input = QLineEdit("0")
        self.azimuth_input.setValidator(QDoubleValidator())
        azimuth_layout.addWidget(self.azimuth_label)
        azimuth_layout.addWidget(self.azimuth_input)
        controls_layout.addLayout(azimuth_layout)

        # Direction radio buttons
        self.direction_group = QButtonGroup()
        self.clockwise = QRadioButton("По часовой")
        self.counterclockwise = QRadioButton("Против часовой")
        self.clockwise.setChecked(True)
        self.direction_group.addButton(self.clockwise)
        self.direction_group.addButton(self.counterclockwise)
        controls_layout.addWidget(self.clockwise)
        controls_layout.addWidget(self.counterclockwise)

        # Action buttons
        self.calculate_btn = QPushButton("Рассчитать")
        self.paste_btn = QPushButton("Вставить из буфера")
        self.add_row_btn = QPushButton("Добавить строку")
        self.delete_row_btn = QPushButton("Удалить строку")
        self.load_excel_btn = QPushButton("Загрузить Excel")

        # Connect button signals
        self.calculate_btn.clicked.connect(self.calculate)
        self.paste_btn.clicked.connect(self.paste_from_clipboard)
        self.add_row_btn.clicked.connect(self.add_row)
        self.delete_row_btn.clicked.connect(self.delete_row)
        self.load_excel_btn.clicked.connect(self.load_excel)

        # Add buttons to controls
        controls_layout.addWidget(self.calculate_btn)
        controls_layout.addWidget(self.paste_btn)
        controls_layout.addWidget(self.add_row_btn)
        controls_layout.addWidget(self.delete_row_btn)
        controls_layout.addWidget(self.load_excel_btn)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)
        self.data_tab.setLayout(layout)

    def setup_result_tab(self):
        """Setup the results visualization tab"""
        # Create a widget to hold the layout
        self.result_widget = QWidget()
        layout = QHBoxLayout(self.result_widget)

        # Left side - vector diagrams
        vector_layout = QVBoxLayout()
        self.plot_widget = VectorPlot(self)
        vector_layout.addWidget(self.plot_widget)

        # Right side - vertical deviation plots
        deviation_layout = QHBoxLayout()
        self.deviation_plots = []
        for i in range(3):
            plot = VerticalDeviationPlot(self)
            self.deviation_plots.append(plot)
            deviation_layout.addWidget(plot)

        # Add both layouts to main layout
        layout.addLayout(vector_layout, stretch=2)
        layout.addLayout(deviation_layout, stretch=1)

        self.result_tab.setLayout(QVBoxLayout())
        self.result_tab.layout().addWidget(self.result_widget)

    def calculate(self):
        """Calculate and display results"""
        try:
            data = self.get_table_data()
            if not data:
                QMessageBox.warning(self, "Предупреждение", "Нет данных для расчета")
                return

            azimuth = float(self.azimuth_input.text())
            is_clockwise = self.clockwise.isChecked()

            # Update vector plots
            self.update_vector_plots(data, azimuth, is_clockwise)

            # Update deviation plots
            self.update_deviation_plots()

            # Switch to vector tab
            self.tabs.setCurrentIndex(1)

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def update_vector_plots(self, data, azimuth, is_clockwise):
        """Update vector diagram plots"""
        # Clear old plots
        while self.vector_container.layout().count():
            item = self.vector_container.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Create new plots
        for i, vector_data in enumerate(data):
            plot = VectorPlot(self)
            plot.plot_vector_diagram(vector_data, azimuth, is_clockwise)
            self.vector_container.layout().addWidget(plot, i // 3, i % 3)

    def update_deviation_plots(self):
        """Update deviation plots"""
        try:
            data = self.get_table_data()
            if not data:
                return

            tolerance = float(self.tolerance_input.text())

            # Clear old plots
            while self.deviation_container.layout().count():
                item = self.deviation_container.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Create new plots
            for i in range(3):
                plot = VerticalDeviationPlot(self)
                plot.plot_deviations(data, i, tolerance)
                self.deviation_container.layout().addWidget(plot)

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))


    def get_table_data(self):
        """Get data from table and return list of VectorData objects"""
        data = []
        for row in range(self.table.rowCount()):
            try:
                name = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
                length1 = float(self.table.item(row, 1).text() if self.table.item(row, 1) else 0)
                length2 = float(self.table.item(row, 2).text() if self.table.item(row, 2) else 0)
                length3 = float(self.table.item(row, 3).text() if self.table.item(row, 3) else 0)

                data.append(VectorData(name, length1, length2, length3))
            except ValueError:
                continue
        return data

    def add_row(self):
        """Add new row to table"""
        current_rows = self.table.rowCount()
        self.table.insertRow(current_rows)

    def delete_row(self):
        """Delete selected row from table"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def paste_from_clipboard(self):
        """Paste data from clipboard"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()

        rows = text.strip().split('\n')
        for row_idx, row in enumerate(rows):
            if row_idx >= self.table.rowCount():
                self.table.insertRow(self.table.rowCount())

            columns = row.strip().split('\t')
            for col_idx, value in enumerate(columns[:4]):  # Limit to 4 columns
                item = QTableWidgetItem(value)
                self.table.setItem(row_idx, col_idx, item)

    def load_excel(self):
        """Load data from Excel file"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл Excel",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if file_name:
            try:
                excel_handler = ExcelHandler()
                data = excel_handler.load_from_excel(file_name)

                # Clear existing table
                self.table.setRowCount(0)

                # Fill table with new data
                for vector_data in data:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(vector_data.name))
                    self.table.setItem(row, 1, QTableWidgetItem(str(vector_data.length1)))
                    self.table.setItem(row, 2, QTableWidgetItem(str(vector_data.length2)))
                    self.table.setItem(row, 3, QTableWidgetItem(str(vector_data.length3)))

            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при загрузке файла: {str(e)}")


def load_excel(self):
    """Load data from Excel file"""
    try:
        excel_handler = ExcelHandler()
        data_list = excel_handler.load_from_excel()  # Убираем передачу file_name

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