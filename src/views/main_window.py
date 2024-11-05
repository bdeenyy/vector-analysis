# src/views/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMessageBox, QScrollArea, QApplication, QGridLayout, QLabel, QLineEdit, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase, QFont
import os

from src.components.styled_widgets import StyledButton
from src.views import IconHelper
from src.views.data_panel import DataPanel
from src.views.control_panel import ControlPanel
from src.views.vector_plot_view import VectorPlotView
from src.views.VerticalDeviationPlot import VerticalDeviationPlot
from src.utils.excel_handler import ExcelHandler
from src.models.vector_data import VectorData


class MainWindow(QMainWindow):
    """
    Главное окно приложения.
    Управляет всеми компонентами и их взаимодействием.
    """

    def __init__(self):
        super().__init__()
        self._init_dependencies()
        self.setup_font()
        self.init_ui()
        self._connect_signals()

    def _init_dependencies(self):
        """Инициализация зависимостей"""
        self.excel_handler = ExcelHandler()

    def setup_font(self):
        """Настройка пользовательского шрифта"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(current_dir)
            font_path = os.path.join(src_dir, 'resources', 'fonts', 'ISOCPEUR.ttf')

            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    # Увеличенный размер шрифта для интерфейса
                    self.custom_font = QFont("ISOCPEUR", 20)  # Увеличили с 10 до 20
                    self.custom_font.setItalic(True)
                    QApplication.setFont(self.custom_font)

                    # Сохраняем путь к шрифту для использования в графиках
                    self.font_path = font_path
            else:
                print(f"Font not found: {font_path}")
        except Exception as e:
            print(f"Error loading font: {str(e)}")

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("Анализ векторных данных")
        self.setGeometry(100, 100, 1200, 800)

        # Создание основного виджета и компоновки
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Создание вкладок
        self.tabs = QTabWidget()

        # Создание и настройка вкладок
        self.setup_data_tab()
        self.setup_vector_tab()
        self.setup_deviation_tab()

        # Добавление вкладок
        self.tabs.addTab(self.data_tab, "Данные")
        self.tabs.addTab(self.vector_tab, "Векторы")
        self.tabs.addTab(self.deviation_tab, "Отклонения")

        # Размещение вкладок в главном окне
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tabs)

    def setup_data_tab(self):
        """Настройка вкладки данных"""
        self.data_tab = QWidget()
        layout = QHBoxLayout(self.data_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Создание панели данных и панели управления
        self.data_panel = DataPanel()
        self.control_panel = ControlPanel()

        layout.addWidget(self.data_panel)
        layout.addWidget(self.control_panel)

    def setup_vector_tab(self):
        """Настройка вкладки векторных диаграмм"""
        self.vector_tab = QWidget()
        layout = QVBoxLayout(self.vector_tab)

        # Панель управления
        control_panel = QHBoxLayout()

        # Кнопка экспорта в PDF
        self.export_pdf_btn = StyledButton("Экспорт в PDF", style_type="default")
        IconHelper.setup_button_with_icon(self.export_pdf_btn, "pdf")
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)
        control_panel.addWidget(self.export_pdf_btn)

        control_panel.addStretch()
        layout.addLayout(control_panel)

        # Область прокрутки для графиков
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Контейнер для графиков
        self.vector_container = QWidget()
        grid = QGridLayout(self.vector_container)
        grid.setSpacing(20)
        grid.setContentsMargins(20, 20, 20, 20)

        scroll.setWidget(self.vector_container)
        layout.addWidget(scroll)

    def setup_deviation_tab(self):
        """Настройка вкладки отклонений"""
        self.deviation_tab = QWidget()
        layout = QVBoxLayout(self.deviation_tab)

        # Панель управления
        controls = QHBoxLayout()

        # Область допуска
        tolerance_layout = QHBoxLayout()
        self.tolerance_label = QLabel("Допустимое отклонение (мм/м):")
        self.tolerance_input = QLineEdit("1.0")
        tolerance_layout.addWidget(self.tolerance_label)
        tolerance_layout.addWidget(self.tolerance_input)
        controls.addLayout(tolerance_layout)

        # Кнопки управления
        self.update_deviation_btn = StyledButton("Обновить графики")
        IconHelper.setup_button_with_icon(self.update_deviation_btn, "refresh")
        self.update_deviation_btn.clicked.connect(self.update_deviation_plots)

        self.export_deviation_pdf_btn = StyledButton("Экспорт в PDF")
        IconHelper.setup_button_with_icon(self.export_deviation_pdf_btn, "pdf")
        self.export_deviation_pdf_btn.clicked.connect(self.export_deviations_to_pdf)

        controls.addWidget(self.update_deviation_btn)
        controls.addWidget(self.export_deviation_pdf_btn)
        controls.addStretch()
        layout.addLayout(controls)

        # Контейнер для графиков отклонений
        self.deviation_container = QWidget()
        self.deviation_container.setLayout(QHBoxLayout())
        layout.addWidget(self.deviation_container)

    def _connect_signals(self):
        """Подключение сигналов компонентов"""
        # Сигналы панели управления
        self.control_panel.calculate_clicked.connect(self._on_calculate)
        self.control_panel.excel_button.clicked.connect(self._on_load_excel)
        self.control_panel.clipboard_button.clicked.connect(self._on_paste)

        # Сигналы изменения вкладок
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_calculate(self):
        """Обработчик нажатия кнопки расчета"""
        try:
            # Получение данных
            data = self._get_table_data()
            if not data:
                raise ValueError("Нет данных для расчета")

            # Получение параметров направления
            direction_values = self.control_panel.get_direction_values()

            # Обновление графиков
            self._update_plots(data, direction_values)

            # Переключение на вкладку векторов
            self.tabs.setCurrentIndex(1)

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Критическая ошибка", f"Неожиданная ошибка: {str(e)}")

    def _get_table_data(self):
        """Получение данных из таблицы"""
        return self.data_panel.get_table().get_data()



    def _update_deviation_plots(self, data):
        """Обновление графиков отклонений"""
        self._clear_container(self.deviation_container)

        for i in range(3):
            plot = VerticalDeviationPlot(self)
            plot.plot_deviations(data, i, 1.0)  # 1.0 - стандартное отклонение
            self.deviation_container.layout().addWidget(plot)

    def _on_load_excel(self):
        """Обработчик загрузки Excel файла"""
        data_list = self.excel_handler.load_from_excel()
        if data_list:
            self.data_panel.get_table().set_data(data_list)

    def _on_paste(self):
        """Обработчик вставки из буфера обмена"""
        clipboard = QApplication.clipboard()
        self.data_panel.get_table().paste_data(clipboard.text())

    def _on_tab_changed(self, index):
        """Обработчик смены вкладки"""
        self.control_panel.setVisible(index == 0)

    def _clear_container(self, container):
        """Очистка контейнера с виджетами"""
        if container and container.layout():
            while container.layout().count():
                item = container.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

    # ---- Методы экспорта ----
    def export_to_pdf(self):
        """Экспорт векторных диаграмм в PDF"""
        if not hasattr(self, '_pdf_handler'):
            from src.utils.pdf_export_handler import PDFExportHandler
            self._pdf_handler = PDFExportHandler(self)

        if self._pdf_handler.export_vectors_to_pdf():
            QMessageBox.information(
                self,
                "Успех",
                "Экспорт векторных диаграмм в PDF выполнен успешно"
            )

    def export_deviations_to_pdf(self):
        """Экспорт графиков отклонений в PDF"""
        if not hasattr(self, '_pdf_handler'):
            from src.utils.pdf_export_handler import PDFExportHandler
            self._pdf_handler = PDFExportHandler(self)

        if self._pdf_handler.export_deviations_to_pdf():
            QMessageBox.information(
                self,
                "Успех",
                "Экспорт графиков отклонений в PDF выполнен успешно"
            )

    # ---- Вспомогательные методы ----
    def _update_plots(self, data, direction_values):
        """Обновление всех графиков"""
        # Обновление векторных диаграмм
        self._update_vector_plots(data, direction_values)

        # Обновление графиков отклонений
        self._update_deviation_plots(data)

    def _update_vector_plots(self, data, direction_values):
        """Обновление векторных диаграмм"""
        self._clear_container(self.vector_container)
        layout = self.vector_container.layout()
        # Убираем отступы у layout контейнера
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        for i, vector_data in enumerate(data):
            plot = VectorPlotView(self)
            plot.setMinimumSize(250, 250)  # Минимальный размер для читаемости
            plot.plot_vector_diagram(
                vector_data,
                direction_values['azimuth'],
                direction_values['is_clockwise']
            )

            # Размещаем в сетке 3 столбца
            row = i // 3
            col = i % 3
            layout.addWidget(plot, row, col, Qt.AlignmentFlag.AlignCenter)

    def update_deviation_plots(self):
        """Обновление графиков отклонений"""
        try:
            data = self.data_panel.get_table().get_data()
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