# src/utils/excel_handler.py
from PyQt6.QtWidgets import QFileDialog, QMessageBox
import pandas as pd
from src.models.vector_data import VectorData


class ExcelHandler:
    @staticmethod
    def load_from_excel():
        """
        Открывает диалоговое окно для выбора Excel файла и загружает векторные данные.
        """
        try:
            dialog = QFileDialog(None)
            dialog.setWindowTitle("Выберите Excel файл")
            dialog.setNameFilter("Excel Files (*.xlsx *.xls)")
            dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
            dialog.setViewMode(QFileDialog.ViewMode.Detail)

            if dialog.exec() == QFileDialog.DialogCode.Accepted:
                file_name = dialog.selectedFiles()[0]
            else:
                return []

            print(f"Selected file: {file_name}")  # Для отладки

            # Чтение Excel файла
            df = pd.read_excel(
                file_name,
                engine='openpyxl'  # Явно указываем движок для xlsx
            )

            # Проверяем наличие данных
            if df.empty:
                QMessageBox.warning(None, "Предупреждение", "Excel файл пуст")
                return []

            # Проверяем количество столбцов
            if len(df.columns) < 4:
                QMessageBox.warning(None, "Предупреждение",
                                    "Excel файл должен содержать минимум 4 столбца:\n"
                                    "Сечение, ОП1, ОП2, ОП3")
                return []

            # Обработка данных
            vector_data_list = []

            # Используем только первые 4 столбца
            df = df.iloc[:, :4]

            for index, row in df.iterrows():
                try:
                    # Преобразуем значения
                    name = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else ""

                    # Получаем числовые значения
                    lengths = []
                    for i in range(1, 4):
                        value = row.iloc[i]
                        if pd.isna(value):
                            lengths.append(0.0)
                        else:
                            try:
                                lengths.append(float(value))
                            except (ValueError, TypeError):
                                lengths.append(0.0)

                    # Пропускаем строки, где все значения нулевые и имя пустое
                    if any(lengths) or name.strip():
                        vector_data = VectorData(
                            name=name,
                            length1=lengths[0],
                            length2=lengths[1],
                            length3=lengths[2]
                        )
                        vector_data_list.append(vector_data)

                except Exception as e:
                    print(f"Ошибка в строке {index + 1}: {str(e)}")
                    continue

            if not vector_data_list:
                QMessageBox.warning(
                    None,
                    "Предупреждение",
                    "Не удалось загрузить данные из файла"
                )
                return []

            print(f"Loaded {len(vector_data_list)} records")  # Для отладки
            return vector_data_list

        except pd.errors.EmptyDataError:
            QMessageBox.critical(None, "Ошибка", "Excel файл пуст")
            return []
        except Exception as e:
            QMessageBox.critical(
                None,
                "Ошибка",
                f"Ошибка при загрузке файла: {str(e)}\n"
                f"Убедитесь, что файл имеет формат .xlsx или .xls"
            )
            return []

    @staticmethod
    def _safe_float_convert(value):
        """
        Безопасно преобразует значение в float.
        """
        try:
            if pd.isna(value):
                return 0.0
            result = float(value)
            return result if not pd.isna(result) else 0.0
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def save_to_excel(vector_data_list, file_path):
        """
        Сохраняет векторные данные в Excel файл.
        """
        try:
            data = []
            for vector_data in vector_data_list:
                data.append({
                    'Сечение': vector_data.name,
                    'ОП1': vector_data.length1,
                    'ОП2': vector_data.length2,
                    'ОП3': vector_data.length3
                })

            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False, engine='openpyxl')

        except Exception as e:
            QMessageBox.critical(
                None,
                "Ошибка",
                f"Ошибка при сохранении файла: {str(e)}"
            )