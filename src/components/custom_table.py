# src/components/custom_table.py
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal
from src.models.vector_data import VectorData


class CustomTable(QTableWidget):
    """
    Кастомный компонент таблицы с расширенным функционалом
    """
    data_changed = pyqtSignal()  # Сигнал об изменении данных

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Настройка внешнего вида таблицы"""
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Сечение", "ОП1", "ОП2", "ОП3"])
        self.setRowCount(2)
        self.horizontalHeader().setStretchLastSection(True)
        self.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #e5e7eb;
            }
            QHeaderView::section {
                background-color: #f9fafb;
                border: none;
                border-bottom: 1px solid #e5e7eb;
                padding: 6px;
            }
        """)

    def connect_signals(self):
        """Подключение сигналов"""
        self.cellChanged.connect(self._on_cell_changed)

    def _on_cell_changed(self, row, col):
        """Обработка изменения ячейки"""
        self.data_changed.emit()

    def add_row(self):
        """Добавить новую строку"""
        self.insertRow(self.rowCount())
        self.data_changed.emit()

    def delete_row(self):
        """Удалить выбранную строку"""
        current_row = self.currentRow()
        if current_row >= 0:
            self.removeRow(current_row)
            self.data_changed.emit()

    def get_cell_text(self, row, col):
        """Получить текст ячейки с проверкой"""
        item = self.item(row, col)
        return item.text() if item else ""

    def get_data(self):
        """Получить данные из таблицы в виде списка VectorData"""
        data = []
        for row in range(self.rowCount()):
            try:
                name = self.get_cell_text(row, 0)
                length1 = float(self.get_cell_text(row, 1) or 0)
                length2 = float(self.get_cell_text(row, 2) or 0)
                length3 = float(self.get_cell_text(row, 3) or 0)

                if any([length1, length2, length3]):  # Пропускаем пустые строки
                    data.append(VectorData(name, length1, length2, length3))
            except ValueError:
                continue  # Пропускаем строки с некорректными данными
        return data

    def paste_data(self, text):
        """Вставить данные из буфера обмена"""
        rows = text.strip().split('\n')
        for row_idx, row in enumerate(rows):
            if row_idx >= self.rowCount():
                self.insertRow(self.rowCount())

            columns = row.strip().split('\t')
            for col_idx, value in enumerate(columns[:4]):
                self.setItem(row_idx, col_idx, QTableWidgetItem(value))

        self.data_changed.emit()

    def set_data(self, data_list):
        """Установить данные из списка VectorData"""
        self.setRowCount(0)
        for vector_data in data_list:
            row = self.rowCount()
            self.insertRow(row)
            self.setItem(row, 0, QTableWidgetItem(str(vector_data.name)))
            self.setItem(row, 1, QTableWidgetItem(str(vector_data.length1)))
            self.setItem(row, 2, QTableWidgetItem(str(vector_data.length2)))
            self.setItem(row, 3, QTableWidgetItem(str(vector_data.length3)))

        self.data_changed.emit()